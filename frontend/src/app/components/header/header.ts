import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, TranslateModule],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {
  private router = inject(Router);
  public authService = inject(AuthService);
  private translateService = inject(TranslateService);

  /**
   * Change la langue de l'application
   * Cette méthode met à jour la langue courante et recharge les traductions
   * @param lang - Le code de la langue (ex: 'fr', 'en')
   */
  switchLanguage(lang: string) {
    this.translateService.use(lang);
  }
}
