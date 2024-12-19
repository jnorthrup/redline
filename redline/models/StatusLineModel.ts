export class StatusLineModel {
    private prompt: string;

    constructor(prompt: string) {
        this.prompt = prompt;
    }

    getPrompt(): string {
        return this.prompt;
    }

    setPrompt(prompt: string) {
        this.prompt = prompt;
    }
}
