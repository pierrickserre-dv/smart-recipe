import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-welcome',
  imports: [RouterOutlet, TranslateModule],
  templateUrl: './welcome.html',
  styleUrl: './welcome.css',
})
export class Welcome {}
