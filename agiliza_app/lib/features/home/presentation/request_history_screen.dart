import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/constants/app_sizes.dart';
import '../../../core/utils/currency_format.dart';
import '../../../core/constants/app_strings.dart';
import '../../../core/widgets/app_back_app_bar.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../data/models/backend_models.dart';
import 'home_providers.dart';
import 'quote_response_screen.dart';
import 'review_submission_screen.dart';

class RequestHistoryScreen extends ConsumerWidget {
  const RequestHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final requestsState = ref.watch(requestHistoryProvider);
    ref.watch(quotesProvider);

    return DefaultTabController(
      length: _statuses.length,
      child: Scaffold(
        appBar: AppBackAppBar(
          title: const Text(AppStrings.requestHistoryTitle),
          bottom: TabBar(
            isScrollable: true,
            tabs: _statuses.map((status) {
              return Tab(text: status.label);
            }).toList(),
          ),
        ),
        body: requestsState.when(
          data: (requests) {
            if (requests.isEmpty) {
              return const EmptyView(
                title: 'No service requests',
                subtitle: 'Submit a request to see it here.',
              );
            }

            return TabBarView(
              children: _statuses.map((status) {
                return _RequestHistoryList(
                  status: status,
                  requests: requests,
                );
              }).toList(),
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => ErrorView(
            message: error.toString(),
            onRetry: () => ref.read(requestHistoryProvider.notifier).refresh(),
          ),
        ),
      ),
    );
  }
}

class _RequestHistoryList extends ConsumerWidget {
  final _RequestStatus status;
  final List<ServiceRequest> requests;

  const _RequestHistoryList({
    required this.status,
    required this.requests,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final quotesState = ref.watch(quotesProvider);

    final entries = requests.where((item) {
      final normalized = item.status.toUpperCase();
      if (status == _RequestStatus.accepted) {
        return normalized == 'ACCEPTED' || normalized == 'SCHEDULED';
      }
      return normalized == status.apiValue;
    }).toList();

    if (entries.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppSizes.lg),
          child: Text(
            'No ${status.label.toLowerCase()} requests yet.',
            style: Theme.of(context).textTheme.bodyLarge,
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    return quotesState.when(
      data: (quotes) {
        return ListView.separated(
          padding: const EdgeInsets.all(AppSizes.md),
          itemCount: entries.length,
          separatorBuilder: (_, __) => const SizedBox(height: AppSizes.md),
          itemBuilder: (context, index) {
            final item = entries[index];
            QuoteResponse? quote;
            for (final q in quotes) {
              if (q.serviceRequestId == item.id) {
                quote = q;
                break;
              }
            }

            return InkWell(
              borderRadius: BorderRadius.circular(20),
              onTap: () => _handleTap(context, ref, item, quote),
              child: Card(
                elevation: 2,
                color: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(AppSizes.md),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 54,
                        height: 54,
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Icon(
                          Icons.home_repair_service,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.title,
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Icon(Icons.category, size: 16, color: Colors.grey[700]),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    item.professional?.fullName ?? item.categoryName,
                                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                          fontWeight: FontWeight.w600,
                                        ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Text(
                              item.description,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: Colors.grey[700],
                                    height: 1.4,
                                  ),
                            ),
                            const SizedBox(height: 14),
                            Row(
                              children: [
                                Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    formatDate(item.scheduledDate ?? item.requestedDate),
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                ),
                                if (item.quotedPrice != null)
                                  Text(
                                    CurrencyFormat.format(item.quotedPrice),
                                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                          fontWeight: FontWeight.w700,
                                        ),
                                  ),
                              ],
                            ),
                            if (status == _RequestStatus.quoted && quote != null) ...[
                              const SizedBox(height: 8),
                              Text(
                                'Tap to view and respond to quote',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: Theme.of(context).colorScheme.primary,
                                      fontWeight: FontWeight.w600,
                                    ),
                              ),
                            ],
                          ],
                        ),
                      ),
                      const SizedBox(width: 10),
                      _StatusBadge(status: status),
                    ],
                  ),
                ),
              ),
            );
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => ErrorView(
        message: error.toString(),
        onRetry: () => ref.read(quotesProvider.notifier).refresh(),
      ),
    );
  }

  void _handleTap(
    BuildContext context,
    WidgetRef ref,
    ServiceRequest item,
    QuoteResponse? quote,
  ) {
    final normalized = item.status.toUpperCase();

    if (normalized == 'QUOTED' && quote != null) {
      context.push(
        '/quote-response',
        extra: QuoteScreenArgs(quote: quote, requestId: item.id),
      );
      return;
    }

    if (normalized == 'COMPLETED') {
      final professionalId = item.professional?.id;
      if (professionalId == null || professionalId.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Professional profile unavailable for review.')),
        );
        return;
      }
      context.push(
        '/review-submission',
        extra: ReviewScreenArgs(
          professionalProfileId: professionalId,
          serviceRequestId: item.id,
        ),
      );
    }
  }
}

class _StatusBadge extends StatelessWidget {
  final _RequestStatus status;

  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final color = _statusColor(status, Theme.of(context).colorScheme);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(30),
      ),
      child: Text(
        status.label,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}

enum _RequestStatus {
  pending,
  quoted,
  accepted,
  completed,
  cancelled,
}

extension _RequestStatusLabel on _RequestStatus {
  String get label {
    switch (this) {
      case _RequestStatus.pending:
        return AppStrings.historyTabPending;
      case _RequestStatus.quoted:
        return AppStrings.historyTabQuoted;
      case _RequestStatus.accepted:
        return 'Accepted';
      case _RequestStatus.completed:
        return AppStrings.historyTabCompleted;
      case _RequestStatus.cancelled:
        return AppStrings.historyTabCancelled;
    }
  }

  String get apiValue => name.toUpperCase();
}

const _statuses = [
  _RequestStatus.pending,
  _RequestStatus.quoted,
  _RequestStatus.accepted,
  _RequestStatus.completed,
  _RequestStatus.cancelled,
];

Color _statusColor(_RequestStatus status, ColorScheme colors) {
  switch (status) {
    case _RequestStatus.pending:
      return colors.primary;
    case _RequestStatus.quoted:
      return Colors.orange;
    case _RequestStatus.accepted:
      return Colors.blue;
    case _RequestStatus.completed:
      return Colors.green;
    case _RequestStatus.cancelled:
      return colors.error;
  }
}

String formatDate(String? value) {
  if (value == null || value.isEmpty) {
    return '';
  }

  try {
    final date = DateTime.parse(value);
    return DateFormat('dd MMM yyyy • hh:mm a').format(date);
  } catch (_) {
    return value;
  }
}
