import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

import { UploadDocumentForm } from "@/components/UploadDocumentForm";

describe("UploadDocumentForm", () => {
  it("renderiza el selector de fichero y el botón de subir", () => {
    render(<UploadDocumentForm token="test-token" />);

    expect(screen.getByLabelText(/documento \(pdf, jpg o png/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /subir documento/i })).toBeInTheDocument();
  });

  it("solo acepta pdf, jpg y png", () => {
    render(<UploadDocumentForm token="test-token" />);

    const input = screen.getByLabelText(/documento \(pdf, jpg o png/i);
    expect(input).toHaveAttribute("accept", "application/pdf,image/jpeg,image/png");
  });
});
