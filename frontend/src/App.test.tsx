import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App', () => {
  it('renders the job board homepage', () => {
    render(<App />);
    expect(screen.getByText('Job Board')).toBeInTheDocument();
  });
});
