THROTTLE_RATES = {
    # Authentication throttles
    'login': '3000/hour',
    'registration': '1000/hour',

    # User profile throttles
    'user_profile': '2000/hour',

    # Transaction throttles
    'transaction_create': '50000/hour',
    'transaction_list': '10000/hour',
}
