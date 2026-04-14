import { Component, input, output } from '@angular/core';
import { RecipeResponse } from '../../core/models/recipe.model';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-recipe-card',
  imports: [TranslateModule],
  templateUrl: './recipe-card.html',
  styleUrl: './recipe-card.css',
})
export class RecipeCard {
  recipe = input.required<RecipeResponse>();

  delete = output<string>();
  selected = output<RecipeResponse>();

  onDelete(event: Event) {
    event.stopPropagation();
    const id = this.recipe().id;
    if (id) {
      this.delete.emit(id);
    }
  }

  onSelect() {
    this.selected.emit(this.recipe());
  }
}
