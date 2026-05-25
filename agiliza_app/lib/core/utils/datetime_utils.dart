/// Builds an ISO-8601 UTC datetime string for Django DateTimeField payloads.
String? buildIsoDateTime(String date, String time) {
  final trimmedDate = date.trim();
  if (trimmedDate.isEmpty) {
    return null;
  }

  var hour = 9;
  var minute = 0;

  final timeTrimmed = time.trim();
  if (timeTrimmed.isNotEmpty) {
    final match = RegExp(r'(\d{1,2}):(\d{2})').firstMatch(timeTrimmed);
    if (match != null) {
      hour = int.parse(match.group(1)!);
      minute = int.parse(match.group(2)!);
    }
  }

  final parts = trimmedDate.split('-');
  if (parts.length != 3) {
    return null;
  }

  final year = int.tryParse(parts[0]);
  final month = int.tryParse(parts[1]);
  final day = int.tryParse(parts[2]);
  if (year == null || month == null || day == null) {
    return null;
  }

  final local = DateTime(year, month, day, hour, minute);
  return local.toUtc().toIso8601String();
}
