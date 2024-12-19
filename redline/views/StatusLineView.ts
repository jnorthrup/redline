import { StatusLineModel } from '../models/StatusLineModel';

export class StatusLineView {
    private element: HTMLElement;

    constructor(element: HTMLElement) {
        this.element = element;
    }

    render(model: StatusLineModel): void {
        this.element.textContent = model.getPrompt();
    }
}
