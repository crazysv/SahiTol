import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import App from './App';

describe('SahiTol Web Application Skeleton', () => {
  it('renders application home view with title and Stitch gate note', () => {
    const { getByText } = render(<App />);
    expect(getByText('SahiTol Console')).toBeDefined();
    expect(getByText(/Stitch Design System Active: Project 245073995801566548/i)).toBeDefined();
    expect(getByText('Recycler Console')).toBeDefined();
    expect(getByText('Admin Quality Dashboard')).toBeDefined();
  });
});
