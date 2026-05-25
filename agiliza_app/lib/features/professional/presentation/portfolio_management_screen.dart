import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../../core/constants/app_sizes.dart';
import '../../../core/network/api_client.dart';
import '../../../core/widgets/app_back_app_bar.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../home/data/models/backend_models.dart';
import '../../home/presentation/home_providers.dart';

class PortfolioManagementScreen extends ConsumerWidget {
  const PortfolioManagementScreen({super.key});

  Future<void> _showAddDialog(BuildContext context, WidgetRef ref) async {
    final titleController = TextEditingController();
    final descriptionController = TextEditingController();
    final picker = ImagePicker();
    XFile? pickedFile;

    final shouldSave = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Add portfolio item'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(labelText: 'Title'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: descriptionController,
                      maxLines: 3,
                      decoration: const InputDecoration(labelText: 'Description'),
                    ),
                    const SizedBox(height: 12),
                    OutlinedButton.icon(
                      onPressed: () async {
                        final image = await picker.pickImage(
                          source: ImageSource.gallery,
                          imageQuality: 85,
                        );
                        if (image != null) {
                          setDialogState(() => pickedFile = image);
                        }
                      },
                      icon: const Icon(Icons.photo_library_outlined),
                      label: Text(
                        pickedFile == null ? 'Choose image' : 'Image selected',
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext, false),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(dialogContext, true),
                  child: const Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );

    if (shouldSave != true || pickedFile == null) {
      titleController.dispose();
      descriptionController.dispose();
      return;
    }

    try {
      final bytes = await pickedFile!.readAsBytes();
      await ref.read(portfolioProvider.notifier).addPortfolioItemFromBytes(
            title: titleController.text.trim(),
            description: descriptionController.text.trim(),
            imageBytes: bytes,
            filename: pickedFile!.name,
          );
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Portfolio item added')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Unable to add portfolio: $e')),
        );
      }
    } finally {
      titleController.dispose();
      descriptionController.dispose();
    }
  }

  String _resolveImageUrl(String path, String baseUrl) {
    if (path.isEmpty) return '';
    if (path.startsWith('http')) return path;
    final host = baseUrl.replaceAll('/api', '');
    if (path.startsWith('/')) {
      return '$host$path';
    }
    return '$host/$path';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final portfolioState = ref.watch(portfolioProvider);
    final baseUrl = ref.read(apiClientProvider).dio.options.baseUrl;

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7F6),
      appBar: const AppBackAppBar(
        title: Text('Portfolio Management'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddDialog(context, ref),
        icon: const Icon(Icons.add_rounded),
        label: const Text('Add Portfolio'),
      ),
      body: portfolioState.when(
        data: (items) {
          if (items.isEmpty) {
            return const EmptyView(
              title: 'No portfolio added yet',
              subtitle: 'Show your previous work to attract more clients.',
            );
          }

          return RefreshIndicator(
            onRefresh: () => ref.read(portfolioProvider.notifier).refresh(),
            child: ListView.separated(
              padding: AppSizes.pagePadding,
              itemCount: items.length,
              separatorBuilder: (_, __) => const SizedBox(height: 14),
              itemBuilder: (context, index) {
                final item = items[index];
                final imageUrl = _resolveImageUrl(item.imageUrl, baseUrl);

                return _PortfolioCard(
                  item: item,
                  imageUrl: imageUrl,
                  onDelete: () async {
                    final confirmed = await showDialog<bool>(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Delete portfolio item'),
                        content: Text('Remove "${item.title}"?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(ctx, false),
                            child: const Text('Cancel'),
                          ),
                          FilledButton(
                            onPressed: () => Navigator.pop(ctx, true),
                            child: const Text('Delete'),
                          ),
                        ],
                      ),
                    );

                    if (confirmed == true) {
                      try {
                        await ref
                            .read(portfolioProvider.notifier)
                            .deletePortfolioItem(item.id);
                      } catch (e) {
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Delete failed: $e')),
                          );
                        }
                      }
                    }
                  },
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => ErrorView(
          message: error.toString(),
          onRetry: () => ref.read(portfolioProvider.notifier).refresh(),
        ),
      ),
    );
  }
}

class _PortfolioCard extends StatelessWidget {
  final PortfolioItem item;
  final String imageUrl;
  final VoidCallback onDelete;

  const _PortfolioCard({
    required this.item,
    required this.imageUrl,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (imageUrl.isNotEmpty)
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
              child: Image.network(
                imageUrl,
                height: 180,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  height: 180,
                  color: Colors.grey.shade200,
                  child: const Icon(Icons.broken_image_outlined),
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 8),
                Text(
                  item.description,
                  style: TextStyle(color: Colors.grey.shade700, height: 1.4),
                ),
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerRight,
                  child: IconButton(
                    onPressed: onDelete,
                    icon: const Icon(Icons.delete_outline),
                    tooltip: 'Delete',
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
