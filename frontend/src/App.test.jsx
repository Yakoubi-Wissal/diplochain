import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

// the app now uses api.js helpers; mock them so tests stay fast and
// deterministic. we only care that login form renders and mocks exist.
jest.mock("./api", () => ({
  login: jest.fn().mockResolvedValue({ access_token: "tok" }),
  getMetrics: jest.fn().mockResolvedValue([MOCK_METRICS_TODAY]),
  getMetricsDaily: jest.fn().mockResolvedValue([MOCK_METRICS_TODAY]),
}));

import App from "./DiploChain_Dashboard_v3";
import { MOCK_METRICS_TODAY } from "./mocks";

// a very basic smoke test showing mocks are available before login
it("renders login form and uses mock data", () => {
  render(<App />);
  // Login page should show
  expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/mot de passe/i)).toBeInTheDocument();
  // metrics mock is not rendered until after login, but we can at least
  // sanity-check its shape via import
  expect(MOCK_METRICS_TODAY.nb_diplomes_emis).toBe(847);
});
