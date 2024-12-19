import { StatusLineController } from './controllers/StatusLineController';

export class StatusLine {
    private controller: StatusLineController;

    constructor(modelName: string) {
        this.controller = new StatusLineController(modelName);
    }

    toString(): string {
        return this.controller.toString();
    }
}
