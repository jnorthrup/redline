import { writeFile, readFile, unlink } from 'fs/promises';
import { MemoryStorage } from './MemoryManager';

export class FileStorage implements MemoryStorage {
  private basePath: string;

  constructor(basePath: string) {
    this.basePath = basePath;
  }

  async save(key: string, data: any): Promise<void> {
    const filePath = `${this.basePath}/${key}.json`;
    await writeFile(filePath, JSON.stringify(data), 'utf-8');
  }

  async load(key: string): Promise<any> {
    try {
      const filePath = `${this.basePath}/${key}.json`;
      const data = await readFile(filePath, 'utf-8');
      return JSON.parse(data);
    } catch (error) {
      return null;
    }
  }

  async clear(): Promise<void> {
    // Implementation depends on your specific needs
    // This is a basic version that would need error handling
    const filePath = `${this.basePath}/history.json`;
    await unlink(filePath).catch(() => {});
  }
}
