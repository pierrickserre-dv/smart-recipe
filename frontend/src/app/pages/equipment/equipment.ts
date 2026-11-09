import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RecipeService } from '../../core/services/recipe.service';

@Component({
  selector: 'app-equipment',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './equipment.html',
  styleUrl: './equipment.css',
})
export class Equipment {
  private recipeService = inject(RecipeService);

  equipment = signal<string[]>([]);
  isLoadingEquipment = signal(false);
  isSavingEquipment = signal(false);
  equipmentError = signal<string | null>(null);

  constructor() {
    this.loadEquipment();
  }

  private loadEquipment(): void {
    this.isLoadingEquipment.set(true);
    this.equipmentError.set(null);
    this.recipeService.getEquipment().subscribe({
      next: (response) => {
        this.equipment.set(response.equipment ?? []);
        this.isLoadingEquipment.set(false);
      },
      error: () => {
        this.isLoadingEquipment.set(false);
        this.equipmentError.set('Unable to load your cooking equipment.');
      },
    });
  }

  addEquipment(raw: string): void {
    if (this.isSavingEquipment()) {
      return;
    }

    const value = raw.trim();
    if (!value) {
      return;
    }

    const next = [...this.equipment()];
    if (next.some((item) => item.toLowerCase() === value.toLowerCase())) {
      return;
    }

    next.push(value);
    this.saveEquipment(next);
  }

  removeEquipment(index: number): void {
    if (this.isSavingEquipment()) {
      return;
    }
    const next = this.equipment().filter((_, i) => i !== index);
    this.saveEquipment(next);
  }

  private saveEquipment(nextEquipment: string[]): void {
    this.isSavingEquipment.set(true);
    this.equipmentError.set(null);
    this.recipeService.updateEquipment(nextEquipment).subscribe({
      next: (response) => {
        this.equipment.set(response.equipment ?? []);
        this.isSavingEquipment.set(false);
      },
      error: () => {
        this.isSavingEquipment.set(false);
        this.equipmentError.set('Unable to save your cooking equipment.');
      },
    });
  }
}
