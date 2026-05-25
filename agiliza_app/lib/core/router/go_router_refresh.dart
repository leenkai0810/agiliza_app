import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_notifier.dart';
import '../auth/auth_state.dart';

/// Notifies [GoRouter] when auth state changes so redirects re-run.
class GoRouterRefresh extends ChangeNotifier {
  GoRouterRefresh(Ref ref) {
    ref.listen<AuthState>(
      authNotifierProvider,
      (_, __) => notifyListeners(),
    );
  }
}
