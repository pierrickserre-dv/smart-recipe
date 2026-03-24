import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Generation } from './generation';

describe('Generation', () => {
  let component: Generation;
  let fixture: ComponentFixture<Generation>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Generation],
    }).compileComponents();

    fixture = TestBed.createComponent(Generation);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
