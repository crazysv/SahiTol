import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import U01_UnitEconomics from './U01_UnitEconomics';

describe('U01 Unit Economics Screen (T039, R-ECON-01, AT-067)', () => {
  it('renders same-lot comparison header, fixture overview, and cards', () => {
    render(
      <MemoryRouter>
        <U01_UnitEconomics />
      </MemoryRouter>
    );

    expect(screen.getByText('U01 Unit Economics')).toBeDefined();
    expect(screen.getByText('Same Material. Different Operating Assumptions.')).toBeDefined();
    expect(screen.getByText('Stripped Copper Cable (Grade A)')).toBeDefined();
    expect(screen.getByText(/Batch Weight:/i)).toBeDefined();
    expect(screen.getByText('Baseline (Manual)')).toBeDefined();
    expect(screen.getByText('SahiTol Optimized')).toBeDefined();
    expect(screen.getByText('Operating Assumptions')).toBeDefined();
    expect(screen.getByText('Unit Economics Waterfall')).toBeDefined();
  });

  it('displays mandatory illustrative disclaimer and 0 paise collector fee guarantee', () => {
    render(
      <MemoryRouter>
        <U01_UnitEconomics />
      </MemoryRouter>
    );

    expect(screen.getByText(/Illustrative calculation fixture/i)).toBeDefined();
    expect(screen.getByText(/We have not measured income uplift/i)).toBeDefined();
    expect(screen.getByText(/Zero Collector Fee: SahiTol levies 0 paise transaction fee/i)).toBeDefined();
    expect(screen.getAllByText(/ECONOMICS_V1/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/chosen demo assumptions/i)).toBeDefined();
  });

  it('uses the documented ECONOMICS_V1 fixture rather than an unstated uplift', () => {
    render(<MemoryRouter><U01_UnitEconomics /></MemoryRouter>);

    expect(screen.getByText('₹350')).toBeDefined();
    expect(screen.getByText('₹470')).toBeDefined();
    expect(screen.getByText('+₹120')).toBeDefined();
    expect(screen.getByText(/₹150\/kg with ₹100 transport and ₹50 handling/i)).toBeDefined();
  });

  it('updates platform calculations dynamically when sliders are changed', () => {
    render(
      <MemoryRouter>
        <U01_UnitEconomics />
      </MemoryRouter>
    );

    // Initial fixture transport discount is -20% (₹100 -> ₹80).
    expect(screen.getByText('-20% Cost')).toBeDefined();

    // Find range input for transport efficiency and change to 50%
    const sliders = screen.getAllByRole('slider');
    expect(sliders.length).toBeGreaterThanOrEqual(3);

    const transportSlider = sliders[0];
    fireEvent.change(transportSlider, { target: { value: '50' } });

    expect(screen.getByText('-50% Cost')).toBeDefined();
  });

  it('toggles switches and updates platform benefits', () => {
    render(
      <MemoryRouter>
        <U01_UnitEconomics />
      </MemoryRouter>
    );

    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes.length).toBeGreaterThanOrEqual(2);

    const smelterCheckbox = checkboxes[1];
    expect(smelterCheckbox).toBeDefined();

    // Toggle off direct smelter linkage
    fireEvent.click(smelterCheckbox);
    // Disabling the stated platform-rate assumption brings platform gross back to baseline.
    expect(screen.getAllByText(/₹1500 Gross/i).length).toBe(2);
  });

  it('permits an unfavourable platform assumption instead of implying a guaranteed benefit', () => {
    render(<MemoryRouter><U01_UnitEconomics /></MemoryRouter>);

    fireEvent.change(screen.getByRole('slider', { name: /platform rate assumption adjustment/i }), { target: { value: '-30' } });
    fireEvent.change(screen.getByRole('slider', { name: /transport efficiency assumption/i }), { target: { value: '-50' } });
    fireEvent.click(screen.getByRole('checkbox', { name: /platform-rate fixture assumption/i }));

    expect(screen.getByText('-₹500')).toBeDefined();
    expect(screen.getByText(/-142.9%/i)).toBeDefined();
  });

  it('switches between same-lot comparison and methodology tabs', () => {
    render(
      <MemoryRouter>
        <U01_UnitEconomics />
      </MemoryRouter>
    );

    const methodologyTab = screen.getByRole('button', { name: /Methodology & Sources/i });
    fireEvent.click(methodologyTab);

    expect(screen.getByText('Mathematical Modeling & Public Sources')).toBeDefined();
    expect(screen.getAllByText(/docs\/23_UNIT_ECONOMICS\.md/i).length).toBeGreaterThanOrEqual(1);

    const backButton = screen.getByRole('button', { name: /Back to Same-Lot Calculator/i });
    fireEvent.click(backButton);

    expect(screen.getByText('Same Material. Different Operating Assumptions.')).toBeDefined();
  });

  it('handles reset scenario and restores baseline defaults', () => {
    render(
      <MemoryRouter>
        <U01_UnitEconomics />
      </MemoryRouter>
    );

    const sliders = screen.getAllByRole('slider');
    fireEvent.change(sliders[0], { target: { value: '10' } });
    expect(screen.getByText('-10% Cost')).toBeDefined();

    const resetButton = screen.getByRole('button', { name: /Reset Scenario/i });
    fireEvent.click(resetButton);

    expect(screen.getByText('-20% Cost')).toBeDefined();
    expect(screen.getByText(/Scenario restored to standard 10 kg benchmark/i)).toBeDefined();
  });
});
