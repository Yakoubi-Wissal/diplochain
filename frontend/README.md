# DiploChain V2 Audit Dashboard 🛠️

A temporary, standalone React interface for testing and reporting DiploChain V2 backend status.

## Purpose
- **Interactive Testing**: Validate Login, Institution, and Student services via the API Gateway.
- **Health Monitoring**: Real-time status check for all 14 microservices.
- **Audit Reporting**: Generate and download a Markdown report for stage supervisors.

## Getting Started

1. **Navigate to the dashboard**:
   ```bash
   cd audit-dashboard
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Access the Dashboard**:
   Open [http://localhost:3001](http://localhost:3001) in your browser.

## Audit Workflow
1. Select your **Role** (Administrator/Institution/Student).
2. Click **Run Full Audit** to execute the verification sequence.
3. Check the **Execution Logs** for detailed step-by-step results.
4. Go to the **Audit Report** tab to download your final report.

> [!NOTE]
> This dashboard communicates with the backend via `http://localhost:8000`. Ensure your Docker containers are UP and healthy before running tests.
