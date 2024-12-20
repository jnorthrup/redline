import { ClientManagement } from './ConsultantPackages/ClientManagement';
import { ProjectManagement } from './ConsultantPackages/ProjectManagement';
import { Reporting } from './ConsultantPackages/Reporting';

class Consultant {
    private clientManagement: ClientManagement;
    private projectManagement: ProjectManagement;
    private reporting: Reporting;

    constructor() {
        this.clientManagement = new ClientManagement();
        this.projectManagement = new ProjectManagement();
        this.reporting = new Reporting();
    }

    // Delegate methods to the appropriate packages
    manageClient() {
        this.clientManagement.manageClient();
    }

    manageProject() {
        this.projectManagement.manageProject();
    }

    generateReport() {
        this.reporting.generateReport();
    }
}
