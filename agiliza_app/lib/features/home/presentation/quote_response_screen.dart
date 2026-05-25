import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_sizes.dart';
import '../../../core/utils/currency_format.dart';
import '../../../core/widgets/app_back_app_bar.dart';
import '../../../core/widgets/error_view.dart';
import '../data/models/backend_models.dart';
import 'home_providers.dart';

class QuoteScreenArgs {
  final QuoteResponse quote;
  final String requestId;

  const QuoteScreenArgs({
    required this.quote,
    required this.requestId,
  });
}

class QuoteResponseScreen extends ConsumerStatefulWidget {
  final QuoteScreenArgs? args;

  const QuoteResponseScreen({super.key, this.args});

  @override
  ConsumerState<QuoteResponseScreen> createState() => _QuoteResponseScreenState();
}

class _QuoteResponseScreenState extends ConsumerState<QuoteResponseScreen> {
  bool _isUpdating = false;

  QuoteScreenArgs? get _args => widget.args;

  Future<void> _respondToQuote(String status) async {
    final args = _args;
    if (args == null) return;

    setState(() => _isUpdating = true);

    try {
      await ref.read(requestHistoryProvider.notifier).updateRequestStatus(
            requestId: args.requestId,
            status: status,
          );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            status == 'ACCEPTED'
                ? 'Quote accepted successfully'
                : 'Request cancelled',
          ),
        ),
      );
      context.pop(true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Unable to update request: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isUpdating = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final args = _args;

    if (args == null) {
      return Scaffold(
        appBar: const AppBackAppBar(title: Text('Quote response')),
        body: ErrorView(
          message: 'No quote was provided for this screen.',
          onRetry: () => context.pop(),
        ),
      );
    }

    final quote = args.quote;
    final professional = quote.professional;
    final professionalName = professional?.fullName ?? 'Professional';
    final avatarUrl = professional?.avatarUrl ?? '';
    final categoryName = professional?.categories.isNotEmpty == true
        ? professional!.categories.first.name
        : 'Service';

    return Scaffold(
      appBar: const AppBackAppBar(
        title: Text('Quote response'),
      ),
      body: SingleChildScrollView(
        padding: AppSizes.pagePadding,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: AppSizes.sm),
            Text('Estimated price', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: AppSizes.xs),
            Text(
              CurrencyFormat.format(double.tryParse(quote.price) ?? 0),
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: AppSizes.lg),
            Row(
              children: [
                _QuoteStat(label: 'Duration', value: quote.duration),
                const SizedBox(width: AppSizes.sm),
                _QuoteStat(label: 'Category', value: categoryName),
              ],
            ),
            const SizedBox(height: AppSizes.xl),
            Text('Message from professional', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: AppSizes.sm),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(AppSizes.md),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(AppSizes.radius),
              ),
              child: Text(
                quote.message.isNotEmpty
                    ? quote.message
                    : 'No additional message provided.',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ),
            const SizedBox(height: AppSizes.xl),
            Text('Professional', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: AppSizes.sm),
            Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                  backgroundImage:
                      avatarUrl.isNotEmpty ? NetworkImage(avatarUrl) : null,
                  child: avatarUrl.isEmpty
                      ? Text(
                          professionalName.isNotEmpty
                              ? professionalName[0].toUpperCase()
                              : 'P',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        )
                      : null,
                ),
                const SizedBox(width: AppSizes.sm),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(professionalName, style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: AppSizes.xs),
                      Text(
                        professional?.role ?? 'Professional',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppSizes.xl),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _isUpdating ? null : () => _respondToQuote('CANCELLED'),
                    child: const Text('Reject'),
                  ),
                ),
                const SizedBox(width: AppSizes.sm),
                Expanded(
                  child: FilledButton(
                    onPressed: _isUpdating ? null : () => _respondToQuote('ACCEPTED'),
                    child: _isUpdating
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Accept'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _QuoteStat extends StatelessWidget {
  final String label;
  final String value;

  const _QuoteStat({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(AppSizes.sm),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(AppSizes.radius),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: AppSizes.xs),
            Text(
              value,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }
}
