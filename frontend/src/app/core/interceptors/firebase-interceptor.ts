import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { environment } from '../../../environments/environment';
import { AuthService } from '../services/auth';
import { switchMap, take } from 'rxjs';

export const firebaseInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  if (req.url.startsWith('/api')) {
    return authService.idToken$.pipe(
      take(1),
      switchMap(token => {
        const route = req.url.replace('/api', '');
        const url = `${environment.apiUrl}${route}`;
        if (token) {
          const headers = req.headers.set('Authorization', `Bearer ${token}`);
          return next(req.clone({ url, headers }));
        } else {
          return next(req.clone({ url }));
        }
      })
    );
  }
  return next(req);
};

// export const firebaseInterceptor: HttpInterceptorFn = (req, next) => {
//   const authService = inject(AuthService);
//   if (req.url.startsWith('/api')) {
//     const token = authService.idToken();
//     const route = req.url.replace('/api', '');
//     const url = `${environment.apiUrl}${route}`;
//     if (token) {
//       const headers = req.headers.set('Authorization', `Bearer ${token}`);
//       return next(req.clone({ url, headers }));
//     } else {
//       return next(req.clone({ url }));
//     }
//   }
//   return next(req);
// };
