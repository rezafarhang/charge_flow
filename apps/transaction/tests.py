from decimal import Decimal
import threading
from django.test import TestCase, TransactionTestCase
from django.db.models import Sum

from apps.users import models as users_models, consts as users_consts
from apps.transaction import models, services


class SimpleTransactionTestCase(TestCase):
    def setUp(self):
        self.admin = users_models.User.objects.create(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_admin=True,
            role=users_consts.UserRole.ADMIN
        )

        self.seller1 = users_models.User.objects.create(
            username='seller1',
            email='seller1@test.com',
            password='seller123',
            role=users_consts.UserRole.SELLER,
        )
        self.seller2 = users_models.User.objects.create(
            username='seller2',
            email='seller2@test.com',
            password='seller123',
            role=users_consts.UserRole.SELLER
        )

        self.wallet1 = models.Wallet.objects.create(user=self.seller1, balance=Decimal('0'))
        self.wallet2 = models.Wallet.objects.create(user=self.seller2, balance=Decimal('0'))

        self.phones = []
        for i in range(10):
            phone_user = users_models.User.objects.create(
                username=f'phone{i}@test.com',
                email=f'phone{i}@test.com',
                password='phone123'
            )
            phone = users_models.PhoneNumber.objects.create(
                phone_number=f'+9891234567{i:02d}',
                user=phone_user,
                balance=Decimal('0')
            )
            self.phones.append(phone)

    def test_simple_workflow(self):
        credit_amount = Decimal('100000')
        total_credits_per_seller = Decimal('0')

        for i in range(5):
            trc = services.CreditRequestService.create_credit_request(
                user=self.seller1,
                amount=credit_amount
            )
            self.assertEqual(trc.status, models.TransactionStatus.PENDING)

            services.CreditRequestService.update_status_credit_request(
                transaction_id=trc.id,
                admin_user=self.admin,
                status=models.TransactionStatus.APPROVED
            )
            total_credits_per_seller += credit_amount

        for i in range(5):
            trc = services.CreditRequestService.create_credit_request(
                user=self.seller2,
                amount=credit_amount
            )
            self.assertEqual(trc.status, models.TransactionStatus.PENDING)

            # Approve credit
            services.CreditRequestService.update_status_credit_request(
                transaction_id=trc.id,
                admin_user=self.admin,
                status=models.TransactionStatus.APPROVED
            )

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet1.balance, total_credits_per_seller)
        self.assertEqual(self.wallet2.balance, total_credits_per_seller)

        charge_amount = Decimal('500')
        num_sales = 1000

        sales_per_seller = num_sales // 2

        for i in range(sales_per_seller):
            phone = self.phones[i % len(self.phones)]
            services.ChargeService.sell_charge(
                user=self.seller1,
                phone_number=phone.phone_number,
                amount=charge_amount
            )

        for i in range(sales_per_seller):
            phone = self.phones[i % len(self.phones)]
            services.ChargeService.sell_charge(
                user=self.seller2,
                phone_number=phone.phone_number,
                amount=charge_amount
            )

        self._verify_accounting()

    def _verify_accounting(self):
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()

        seller1_credits = models.Transaction.objects.filter(
            to_wallet=self.wallet1,
            status=models.TransactionStatus.APPROVED,
            from_type=models.SourceType.USER
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        seller1_sales = models.Transaction.objects.filter(
            from_wallet=self.wallet1,
            status=models.TransactionStatus.APPROVED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        expected_balance_seller1 = seller1_credits - seller1_sales

        seller2_credits = models.Transaction.objects.filter(
            to_wallet=self.wallet2,
            status=models.TransactionStatus.APPROVED,
            from_type=models.SourceType.USER
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        seller2_sales = models.Transaction.objects.filter(
            from_wallet=self.wallet2,
            status=models.TransactionStatus.APPROVED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        expected_balance_seller2 = seller2_credits - seller2_sales

        self.assertEqual(
            self.wallet1.balance,
            expected_balance_seller1,
            f"Seller1 balance mismatch: {self.wallet1.balance} != {expected_balance_seller1}"
        )
        self.assertEqual(
            self.wallet2.balance,
            expected_balance_seller2,
            f"Seller2 balance mismatch: {self.wallet2.balance} != {expected_balance_seller2}"
        )

        total_phone_balance = users_models.PhoneNumber.objects.aggregate(
            total=Sum('balance')
        )['total'] or Decimal('0')

        total_sales = seller1_sales + seller2_sales

        self.assertEqual(
            total_phone_balance,
            total_sales,
            f"Phone balance mismatch: {total_phone_balance} != {total_sales}"
        )

        print(f"Seller 1 - Credits: {seller1_credits}, Sales: {seller1_sales}, Balance: {self.wallet1.balance}")
        print(f"Seller 2 - Credits: {seller2_credits}, Sales: {seller2_sales}, Balance: {self.wallet2.balance}")
        print(f"Total Phone Balance: {total_phone_balance}")
        print(f"Total Sales: {total_sales}")


class AccountingConsistencyTestCase(TestCase):
    """
    - No double credit approval
    - No negative balance
    - Transaction logs are accurate
    """

    def setUp(self):
        self.admin = users_models.User.objects.create(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_admin=True,
            role=users_consts.UserRole.ADMIN
        )

        self.seller = users_models.User.objects.create(
            username='seller',
            email='seller@test.com',
            password='seller123',
            role=users_consts.UserRole.SELLER
        )

        self.wallet = models.Wallet.objects.create(user=self.seller, balance=Decimal('0'))

        phone_user = users_models.User.objects.create(
            username='phone_user',
            email='phone@test.com',
            password='phone123'
        )
        self.phone = users_models.PhoneNumber.objects.create(
            phone_number='+989123456789',
            user=phone_user,
            balance=Decimal('0')
        )

    def test_no_double_credit_approval(self):
        trc = services.CreditRequestService.create_credit_request(
            user=self.seller,
            amount=Decimal('10000')
        )

        services.CreditRequestService.update_status_credit_request(
            transaction_id=trc.id,
            admin_user=self.admin,
            status=models.TransactionStatus.APPROVED
        )

        self.wallet.refresh_from_db()
        balance_after_first_approval = self.wallet.balance
        self.assertEqual(balance_after_first_approval, Decimal('10000'))

        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            services.CreditRequestService.update_status_credit_request(
                transaction_id=trc.id,
                admin_user=self.admin,
                status=models.TransactionStatus.APPROVED
            )

        # Verify balance hasn't changed
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, balance_after_first_approval)

    def test_no_negative_balance(self):
        trc = services.CreditRequestService.create_credit_request(
            user=self.seller,
            amount=Decimal('1000')
        )
        services.CreditRequestService.update_status_credit_request(
            transaction_id=trc.id,
            admin_user=self.admin,
            status=models.TransactionStatus.APPROVED
        )

        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError) as context:
            services.ChargeService.sell_charge(
                user=self.seller,
                phone_number=self.phone.phone_number,
                amount=Decimal('1500')
            )

        # Verify balance is still 1000
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1000'))

    def test_transaction_logs_accuracy(self):
        credit_amount = Decimal('5000')
        trc1 = services.CreditRequestService.create_credit_request(
            user=self.seller,
            amount=credit_amount
        )

        # Verify transaction log
        self.assertEqual(trc1.from_user, self.seller)
        self.assertEqual(trc1.to_wallet, self.wallet)
        self.assertEqual(trc1.amount, credit_amount)
        self.assertEqual(trc1.status, models.TransactionStatus.PENDING)

        services.CreditRequestService.update_status_credit_request(
            transaction_id=trc1.id,
            admin_user=self.admin,
            status=models.TransactionStatus.APPROVED
        )

        trc1.refresh_from_db()
        self.assertEqual(trc1.status, models.TransactionStatus.APPROVED)
        self.assertEqual(trc1.updated_by, self.admin)

        charge_amount = Decimal('1000')
        trc2 = services.ChargeService.sell_charge(
            user=self.seller,
            phone_number=self.phone.phone_number,
            amount=charge_amount
        )

        self.assertEqual(trc2.from_wallet, self.wallet)
        self.assertEqual(trc2.to_phone, self.phone)
        self.assertEqual(trc2.amount, charge_amount)
        self.assertEqual(trc2.status, models.TransactionStatus.APPROVED)

        total_transactions = models.Transaction.objects.count()
        self.assertEqual(total_transactions, 2)


class ConcurrentTransactionTestCase(TransactionTestCase):
    """
    - Multiple concurrent charge sales
    - Multiple concurrent credit approvals
    - Verify no race conditions
    - Verify accounting consistency
    """

    def setUp(self):
        self.admin = users_models.User.objects.create(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_admin=True,
            role=users_consts.UserRole.ADMIN
        )

        self.sellers = []
        self.wallets = []
        for i in range(5):
            seller = users_models.User.objects.create(
                username=f'seller{i}',
                email=f'seller{i}@test.com',
                password='seller123',
                role=users_consts.UserRole.SELLER
            )
            wallet = models.Wallet.objects.create(user=seller, balance=Decimal('0'))
            self.sellers.append(seller)
            self.wallets.append(wallet)

        self.phones = []
        for i in range(20):
            phone_user = users_models.User.objects.create(
                username=f'phone_user_{i}',
                email=f'phone{i}@test.com',
                password='phone123'
            )
            phone = users_models.PhoneNumber.objects.create(
                phone_number=f'+9891234567{i:02d}',
                user=phone_user,
                balance=Decimal('0')
            )
            self.phones.append(phone)

        self.errors = []
        self.error_lock = threading.Lock()

    def _record_error(self, error_msg):
        with self.error_lock:
            self.errors.append(error_msg)

    def test_concurrent_charge_sales(self):
        credit_amount = Decimal('100000')
        for seller, wallet in zip(self.sellers, self.wallets):
            trc = services.CreditRequestService.create_credit_request(
                user=seller,
                amount=credit_amount
            )
            services.CreditRequestService.update_status_credit_request(
                transaction_id=trc.id,
                admin_user=self.admin,
                status=models.TransactionStatus.APPROVED
            )

        for wallet in self.wallets:
            wallet.refresh_from_db()
            self.assertEqual(wallet.balance, credit_amount)

        charge_amount = Decimal('500')
        sales_per_seller = 100
        threads = []

        def sell_charges(seller, num_sales):
            try:
                for i in range(num_sales):
                    phone = self.phones[i % len(self.phones)]
                    services.ChargeService.sell_charge(
                        user=seller,
                        phone_number=phone.phone_number,
                        amount=charge_amount
                    )
            except Exception as e:
                self._record_error(f"Seller {seller.username} error: {str(e)}")

        for seller in self.sellers:
            thread = threading.Thread(
                target=sell_charges,
                args=(seller, sales_per_seller)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if self.errors:
            print(self.errors)
            self.fail(f"Errors occurred during concurrent sales: {self.errors}")

        total_sales = Decimal('0')
        for i, wallet in enumerate(self.wallets):
            wallet.refresh_from_db()

            expected_balance = credit_amount - (charge_amount * sales_per_seller)

            self.assertEqual(
                wallet.balance,
                expected_balance,
                f"Seller {i} balance mismatch: {wallet.balance} != {expected_balance}"
            )

            total_sales += (charge_amount * sales_per_seller)

        total_phone_balance = users_models.PhoneNumber.objects.aggregate(
            total=Sum('balance')
        )['total'] or Decimal('0')

        self.assertEqual(
            total_phone_balance,
            total_sales,
            f"Total phone balance mismatch: {total_phone_balance} != {total_sales}"
        )

    def test_concurrent_same_seller_sales(self):
        seller = self.sellers[0]
        wallet = self.wallets[0]

        credit_amount = Decimal('100000')
        trc = services.CreditRequestService.create_credit_request(
            user=seller,
            amount=credit_amount
        )
        services.CreditRequestService.update_status_credit_request(
            transaction_id=trc.id,
            admin_user=self.admin,
            status=models.TransactionStatus.APPROVED
        )

        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, credit_amount)

        charge_amount = Decimal('500')
        num_concurrent_sales = 150
        threads = []
        success_count = [0]  # Use list for mutable counter
        lock = threading.Lock()

        def sell_charge_worker(seller_user, phone_num):
            try:
                services.ChargeService.sell_charge(
                    user=seller_user,
                    phone_number=phone_num,
                    amount=charge_amount
                )
                with lock:
                    success_count[0] += 1
            except Exception as e:
                self._record_error(f"Expected error: {str(e)}")

        for i in range(num_concurrent_sales):
            phone = self.phones[i % len(self.phones)]
            thread = threading.Thread(
                target=sell_charge_worker,
                args=(seller, phone.phone_number)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        wallet.refresh_from_db()

        self.assertGreaterEqual(
            wallet.balance,
            Decimal('0'),
            "Wallet balance went negative!"
        )

        expected_successful_sales = int(credit_amount / charge_amount)
        expected_balance = credit_amount - (charge_amount * success_count[0])

        self.assertEqual(
            wallet.balance,
            expected_balance,
            f"Balance mismatch: {wallet.balance} != {expected_balance}"
        )

        self.assertLessEqual(
            success_count[0],
            expected_successful_sales,
            f"More sales than possible: {success_count[0]} > {expected_successful_sales}"
        )

    def test_concurrent_credit_approvals(self):
        seller = self.sellers[0]
        wallet = self.wallets[0]

        # Create 10 credit requests
        credit_amount = Decimal('10000')
        credit_requests = []

        for i in range(10):
            trc = services.CreditRequestService.create_credit_request(
                user=seller,
                amount=credit_amount
            )
            credit_requests.append(trc)

        threads = []
        approval_count = [0]
        lock = threading.Lock()

        def approve_worker(trc_id):
            try:
                services.CreditRequestService.update_status_credit_request(
                    transaction_id=trc_id,
                    admin_user=self.admin,
                    status=models.TransactionStatus.APPROVED
                )
                with lock:
                    approval_count[0] += 1
            except Exception:
                pass

        for trc in credit_requests:
            for _ in range(3):
                thread = threading.Thread(
                    target=approve_worker,
                    args=(trc.id,)
                )
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(
            approval_count[0],
            10,
            f"Approval count mismatch: {approval_count[0]} != 10"
        )

        wallet.refresh_from_db()
        expected_balance = credit_amount * 10

        self.assertEqual(
            wallet.balance,
            expected_balance,
            f"Wallet balance mismatch: {wallet.balance} != {expected_balance}"
        )

        approved_count = models.Transaction.objects.filter(
            id__in=[trc.id for trc in credit_requests],
            status=models.TransactionStatus.APPROVED
        ).count()

        self.assertEqual(approved_count, 10)
