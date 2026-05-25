import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/constants/app_strings.dart';
import '../../../core/network/api_client.dart';
final professionalDashboardProvider = FutureProvider.autoDispose<ProfessionalDashboard>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  final response = await apiClient.get<Map<String, dynamic>>(
    AppStrings.professionalDashboardEndpoint,
  );

  final data = response.data ?? {};

  final upcomingAppointments = (data['upcoming_appointments'] as List<dynamic>?)
          ?.map((item) => ProfessionalAppointment(
                id: item['id'] as String? ?? '',
                title: item['title'] as String? ?? 'Appointment',
                date: item['scheduled_date'] as String? ?? item['requested_date'] as String? ?? '',
                status: item['status'] as String? ?? '',
                address: item['address'] as String? ?? '',
              ))
          .toList() ?? [];

  final recentReviews = (data['recent_reviews'] as List<dynamic>?)
          ?.map((item) => ProfessionalReview(
                id: item['id'] as String? ?? '',
                rating: (item['rating'] as num?)?.toDouble() ?? 0.0,
                comment: item['comment'] as String? ?? '',
                createdAt: item['created_at'] as String? ?? '',
              ))
          .toList() ?? [];

  return ProfessionalDashboard(
    fullName: data['full_name'] as String? ?? 'Your Business',
    isVerified: data['is_verified'] as bool? ?? false,
    online: data['online'] as bool? ?? false,
    averageRating: (data['average_rating'] as num?)?.toDouble() ?? 0.0,
    pendingRequests: data['pending_requests'] as int? ?? 0,
    activeJobs: data['active_jobs'] as int? ?? 0,
    completedJobs: data['completed_jobs'] as int? ?? 0,
    monthlyEarnings: (data['monthly_earnings'] as num?)?.toInt() ?? 0,
    upcomingAppointments: upcomingAppointments,
    recentReviews: recentReviews,
  );
});

class ProfessionalDashboard {
  final String fullName;
  final bool isVerified;
  final bool online;
  final double averageRating;
  final int pendingRequests;
  final int activeJobs;
  final int completedJobs;
  final int monthlyEarnings;
  final List<ProfessionalAppointment> upcomingAppointments;
  final List<ProfessionalReview> recentReviews;

  ProfessionalDashboard({
    required this.fullName,
    required this.isVerified,
    required this.online,
    required this.averageRating,
    required this.pendingRequests,
    required this.activeJobs,
    required this.completedJobs,
    required this.monthlyEarnings,
    required this.upcomingAppointments,
    required this.recentReviews,
  });
}

class ProfessionalAppointment {
  final String id;
  final String title;
  final String date;
  final String status;
  final String address;

  ProfessionalAppointment({
    required this.id,
    required this.title,
    required this.date,
    required this.status,
    required this.address,
  });
}

class ProfessionalReview {
  final String id;
  final double rating;
  final String comment;
  final String createdAt;

  ProfessionalReview({
    required this.id,
    required this.rating,
    required this.comment,
    required this.createdAt,
  });
}

