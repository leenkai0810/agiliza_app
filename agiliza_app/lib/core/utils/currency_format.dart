import 'package:intl/intl.dart';

/// USD formatting used across the app.
class CurrencyFormat {
  CurrencyFormat._();

  static const String symbol = '\$';
  static const String locale = 'en_US';

  static String format(num? amount) {
    if (amount == null) return '${symbol}0';
    final value = amount is double ? amount : amount.toDouble();
    return NumberFormat.currency(
      locale: locale,
      symbol: symbol,
      decimalDigits: value == value.truncateToDouble() ? 0 : 2,
    ).format(value);
  }

  static String perHour(num rate) => '${format(rate)}/hr';

  static String inputPrefix() => '$symbol ';
}
