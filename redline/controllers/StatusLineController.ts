import { StatusLineModel } from '../models/StatusLineModel';
import { StatusLineView } from '../views/StatusLineView';

export class StatusLineController {
    private model: StatusLineModel;
    private view: StatusLineView;

    constructor(modelName: string) {
        this.model = new StatusLineModel(modelName);
        this.view = new StatusLineView();
    }

    toString(): string {
        return this.view.render(this.model.modelName);
    }
}
