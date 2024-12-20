import { Observable } from 'rxjs';

export interface MemoryStorage {
  save(key: string, data: any): Promise<void>;
  load(key: string): Promise<any>;
  clear(): Promise<void>;
}

export class MemoryManager {
  private persistentStorage: MemoryStorage;
  private contextStorage: MemoryStorage;
  private conversationHistory: string[] = [];

  constructor(
    persistentStorage: MemoryStorage,
    contextStorage: MemoryStorage
  ) {
    this.persistentStorage = persistentStorage;
    this.contextStorage = contextStorage;
  }

  async savePersistentData(key: string, data: any): Promise<void> {
    await this.persistentStorage.save(key, data);
  }

  async loadPersistentData(key: string): Promise<any> {
    return await this.persistentStorage.load(key);
  }

  addToHistory(message: string): void {
    this.conversationHistory.push(message);
    this.contextStorage.save('history', this.conversationHistory);
  }

  async getConversationHistory(): Promise<string[]> {
    return await this.contextStorage.load('history') || [];
  }

  async clearHistory(): Promise<void> {
    this.conversationHistory = [];
    await this.contextStorage.clear();
  }
}
