import { describe, it, expect } from 'vitest';

describe('HttpClient', () => {
  it('should be defined and exportable', async () => {
    const { httpClient } = await import('../index');
    expect(httpClient).toBeDefined();
    expect(typeof httpClient.get).toBe('function');
    expect(typeof httpClient.post).toBe('function');
    expect(typeof httpClient.put).toBe('function');
    expect(typeof httpClient.patch).toBe('function');
    expect(typeof httpClient.delete).toBe('function');
    expect(typeof httpClient.uploadFile).toBe('function');
  });

  it('should have correct method signatures', async () => {
    const { httpClient } = await import('../index');
    
    // Test that methods exist and are functions
    expect(httpClient.get).toBeInstanceOf(Function);
    expect(httpClient.post).toBeInstanceOf(Function);
    expect(httpClient.put).toBeInstanceOf(Function);
    expect(httpClient.patch).toBeInstanceOf(Function);
    expect(httpClient.delete).toBeInstanceOf(Function);
    expect(httpClient.uploadFile).toBeInstanceOf(Function);
  });
});