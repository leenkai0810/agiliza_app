import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/auth/auth_notifier.dart';
import '../../../core/auth/auth_role.dart';
import '../../../core/constants/app_sizes.dart';
import '../../../core/constants/app_strings.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _passwordVisible = false;
  String? _loginError;

  String? _validateEmail(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Enter your email address';
    }
    final emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    if (!emailRegex.hasMatch(value.trim())) {
      return 'Enter a valid email address';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Enter your password';
    }
    if (value.length < 6) {
      return 'Password must be at least 6 characters';
    }
    return null;
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();

    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
      _loginError = null;
    });

    try {
      final authNotifier = ref.read(authNotifierProvider.notifier);

      final result = await authNotifier.login(
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
      );

      if (!mounted) return;

      final bool success = result['success'] == true;

      if (success) {
        final authState = ref.read(authNotifierProvider);

        final targetRoute =
            authState.role == UserRole.professional
                ? '/professional-root'
                : '/home';

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['message']?.toString() ?? 'Login successful',
            ),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
          ),
        );

        context.go(targetRoute);
      } else {
        final errorMessage =
            result['message']?.toString() ??
            'Invalid email or password';

        setState(() {
          _loginError = errorMessage;
        });
      }
    } catch (e) {
      if (!mounted) return;

      String errorMessage = 'Something went wrong. Please try again.';

      final error = e.toString().toLowerCase();

      if (error.contains('socket')) {
        errorMessage = 'No internet connection';
      } else if (error.contains('timeout')) {
        errorMessage = 'Request timed out';
      } else if (error.contains('401')) {
        errorMessage = 'Invalid email or password';
      }

      setState(() {
        _loginError = errorMessage;
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
  void _handleSocialSignIn(String provider) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Continue with $provider coming soon')),
    );
  }

  void _handleForgotPassword() {
    final email = _emailController.text.trim();
    final message = email.isEmpty
        ? 'Enter your email to reset password'
        : 'Password reset link sent to $email';
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currentError = _loginError;
    final isLoading = _isLoading;

    return Scaffold(
      backgroundColor: theme.colorScheme.surfaceVariant,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: AppSizes.md),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Card(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppSizes.radius),
                  ),
                  elevation: 8,
                  child: Padding(
                    padding: const EdgeInsets.all(AppSizes.lg),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            AppStrings.loginTitle,
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: AppSizes.sm),
                          Text(
                            AppStrings.loginSubtitle,
                            style: theme.textTheme.bodyMedium,
                          ),
                          const SizedBox(height: AppSizes.xl),
                          TextFormField(
                            controller: _emailController,
                            keyboardType: TextInputType.emailAddress,
                            autofillHints: const [AutofillHints.email],
                            decoration: const InputDecoration(
                              labelText: 'Email',
                              hintText: 'name@example.com',
                            ),
                            validator: _validateEmail,
                          ),
                          const SizedBox(height: AppSizes.md),
                          TextFormField(
                            controller: _passwordController,
                            obscureText: !_passwordVisible,
                            decoration: InputDecoration(
                              labelText: 'Password',
                              hintText: 'Enter your password',
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _passwordVisible
                                      ? Icons.visibility
                                      : Icons.visibility_off,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _passwordVisible = !_passwordVisible;
                                  });
                                },
                              ),
                            ),
                            validator: _validatePassword,
                          ),
                          if (currentError != null) ...[
                            const SizedBox(height: AppSizes.sm),
                            Container(
                              padding: const EdgeInsets.all(AppSizes.sm),
                              decoration: BoxDecoration(
                                color: theme.colorScheme.errorContainer,
                                borderRadius: BorderRadius.circular(
                                  AppSizes.radius,
                                ),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(
                                    Icons.error_outline,
                                    color: theme.colorScheme.onErrorContainer,
                                    size: 20,
                                  ),
                                  const SizedBox(width: AppSizes.sm),
                                  Expanded(
                                    child: Text(
                                      currentError,
                                      style: theme.textTheme.bodySmall
                                          ?.copyWith(
                                            color: theme
                                                .colorScheme
                                                .onErrorContainer,
                                          ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          const SizedBox(height: AppSizes.sm),
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton(
                              onPressed: _handleForgotPassword,
                              child: Text(AppStrings.forgotPassword),
                            ),
                          ),
                          const SizedBox(height: AppSizes.md),
                          FilledButton(
                            onPressed: isLoading ? null : _submit,
                            child: isLoading
                                ? const SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2.2,
                                      color: Colors.white,
                                    ),
                                  )
                                : const Text(AppStrings.loginButton),
                          ),
                          const SizedBox(height: AppSizes.md),
                          Row(
                            children: [
                              const Expanded(child: Divider()),
                              Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: AppSizes.sm,
                                ),
                                child: Text(
                                  AppStrings.orContinueWith,
                                  style: theme.textTheme.bodySmall,
                                ),
                              ),
                              const Expanded(child: Divider()),
                            ],
                          ),
                          const SizedBox(height: AppSizes.md),
                          OutlinedButton.icon(
                            icon: const Icon(Icons.g_translate),
                            label: Text(AppStrings.signInWithGoogle),
                            onPressed: () => _handleSocialSignIn('Google'),
                          ),
                          const SizedBox(height: AppSizes.sm),
                          OutlinedButton.icon(
                            icon: const Icon(Icons.apple),
                            label: Text(AppStrings.signInWithApple),
                            onPressed: () => _handleSocialSignIn('Apple'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: AppSizes.lg),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(AppStrings.createAccountPrompt),
                    TextButton(
                      onPressed: () => context.go('/signup'),
                      child: const Text(AppStrings.createAccountAction),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
