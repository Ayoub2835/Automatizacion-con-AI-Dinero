import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

import { RemindButton } from "@/components/RemindButton";

describe("RemindButton", () => {
  it("renderiza el botón de reenvío", () => {
    render(<RemindButton campaignId="campaign-1" />);

    expect(
      screen.getByRole("button", { name: /reenviar recordatorio a pendientes/i }),
    ).toBeInTheDocument();
  });
});
