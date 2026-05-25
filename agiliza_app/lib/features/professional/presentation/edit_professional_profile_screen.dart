import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/constants/app_sizes.dart';
import '../../../core/utils/currency_format.dart';
import '../../../core/constants/app_strings.dart';
import '../../../core/widgets/app_back_app_bar.dart';
import '../../../core/widgets/error_view.dart';
import '../../home/data/models/backend_models.dart';
import '../../home/presentation/home_providers.dart';

class EditProfessionalProfileScreen extends ConsumerStatefulWidget {
  const EditProfessionalProfileScreen({super.key});

  @override
  ConsumerState<EditProfessionalProfileScreen> createState() =>
      _EditProfessionalProfileScreenState();
}

class _EditProfessionalProfileScreenState
    extends ConsumerState<EditProfessionalProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _bioController = TextEditingController();
  final _experienceController = TextEditingController();
  final _hourlyRateController = TextEditingController();
  final _serviceRadiusController = TextEditingController();
  final _addressController = TextEditingController();

  List<ServiceCategory> _categories = [];
  final Set<String> _selectedCategoryIds = {};
  bool _isSaving = false;
  bool _initialized = false;

  @override
  void dispose() {
    _bioController.dispose();
    _experienceController.dispose();
    _hourlyRateController.dispose();
    _serviceRadiusController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  void _populateForm(ProfessionalProfile profile, List<ServiceCategory> categories) {
    if (_initialized) return;
    _initialized = true;
    _bioController.text = profile.bio;
    _experienceController.text = profile.yearsExperience.toString();
    _hourlyRateController.text = profile.hourlyRate.toString();
    _serviceRadiusController.text = profile.serviceRadiusKm.toString();
    _addressController.text = profile.address;
    _categories = categories;
    _selectedCategoryIds
      ..clear()
      ..addAll(profile.categories.map((c) => c.id));
  }

  Future<void> _submitProfile() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_selectedCategoryIds.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Select at least one service category.')),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      await ref.read(myProfessionalProfileProvider.notifier).updateProfile(
            bio: _bioController.text.trim(),
            yearsExperience: int.parse(_experienceController.text.trim()),
            hourlyRate: double.parse(_hourlyRateController.text.trim()),
            serviceRadiusKm: int.parse(_serviceRadiusController.text.trim()),
            address: _addressController.text.trim(),
            categoryIds: _selectedCategoryIds.toList(),
          );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile changes saved successfully.')),
      );
      Navigator.of(context).pop(true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Unable to save profile: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileState = ref.watch(myProfessionalProfileProvider);
    final categoriesState = ref.watch(categoriesProvider);

    return Scaffold(
      appBar: const AppBackAppBar(
        title: Text(AppStrings.editProfileTitle),
      ),
      body: profileState.when(
        data: (profile) {
          return categoriesState.when(
            data: (categories) {
              _populateForm(profile, categories);

              return SingleChildScrollView(
                padding: AppSizes.pagePadding,
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        AppStrings.editProfileSubtitle,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      const SizedBox(height: AppSizes.lg),
                      TextFormField(
                        controller: _bioController,
                        maxLines: 5,
                        decoration: const InputDecoration(
                          labelText: AppStrings.bioLabel,
                          hintText:
                              'Describe your expertise, approach, and signature services.',
                          alignLabelWithHint: true,
                        ),
                        validator: (value) {
                          if (value == null || value.trim().length < 20) {
                            return 'Please enter a more detailed bio.';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSizes.md),
                      TextFormField(
                        controller: _experienceController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: AppStrings.experienceLabel,
                          hintText: 'Years of experience',
                        ),
                        validator: (value) {
                          final parsed = int.tryParse(value ?? '');
                          if (parsed == null || parsed < 0) {
                            return 'Enter a valid experience value.';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSizes.md),
                      TextFormField(
                        controller: _hourlyRateController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: InputDecoration(
                          labelText: AppStrings.hourlyRateLabel,
                          hintText: 'e.g. 65',
                          prefixText: CurrencyFormat.inputPrefix(),
                        ),
                        validator: (value) {
                          final parsed = double.tryParse(value ?? '');
                          if (parsed == null || parsed <= 0) {
                            return 'Enter a valid hourly rate.';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSizes.md),
                      TextFormField(
                        controller: _serviceRadiusController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: AppStrings.serviceRadiusLabel,
                          hintText: 'e.g. 15',
                          suffixText: AppStrings.serviceRadiusSuffix,
                        ),
                        validator: (value) {
                          final parsed = int.tryParse(value ?? '');
                          if (parsed == null || parsed < 0) {
                            return 'Enter a valid service radius.';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSizes.md),
                      TextFormField(
                        controller: _addressController,
                        maxLines: 2,
                        decoration: const InputDecoration(
                          labelText: AppStrings.addressLabel,
                          hintText: 'Service address or operating area',
                        ),
                        validator: (value) {
                          if (value == null || value.trim().length < 10) {
                            return 'Enter a valid address.';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSizes.md),
                      Text(
                        AppStrings.categoryLabel,
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      const SizedBox(height: AppSizes.sm),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: _categories.map((category) {
                          final selected = _selectedCategoryIds.contains(category.id);
                          return FilterChip(
                            label: Text(category.name),
                            selected: selected,
                            onSelected: (value) {
                              setState(() {
                                if (value) {
                                  _selectedCategoryIds.add(category.id);
                                } else {
                                  _selectedCategoryIds.remove(category.id);
                                }
                              });
                            },
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: AppSizes.xl),
                      FilledButton(
                        onPressed: _isSaving ? null : _submitProfile,
                        child: _isSaving
                            ? const SizedBox(
                                height: 22,
                                width: 22,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Text(AppStrings.saveProfileButton),
                      ),
                    ],
                  ),
                ),
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => ErrorView(
              message: error.toString(),
              onRetry: () => ref.read(categoriesProvider.notifier).refresh(),
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => ErrorView(
          message: error.toString(),
          onRetry: () => ref.read(myProfessionalProfileProvider.notifier).refresh(),
        ),
      ),
    );
  }
}
