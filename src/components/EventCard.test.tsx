import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventCard } from "@/components/EventCard";
import { events } from "@/lib/data";

describe("EventCard", () => {
  it("renders core event fields and actions", () => {
    render(<EventCard event={events[0]} />);

    expect(screen.getByRole("heading", { name: /Hikari Loop Spring Signal/ })).toBeInTheDocument();
    expect(screen.getByText("Hikari Loop")).toBeInTheDocument();
    expect(screen.getByText("已開賣")).toBeInTheDocument();
    expect(screen.getByText(/Taipei \/ Legacy Taipei/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "查看詳情" })).toHaveAttribute(
      "href",
      "/events/hikari-loop-2026-taipei",
    );
    expect(screen.getByRole("link", { name: "官方購票" })).toHaveAttribute(
      "href",
      "https://example.org/tickets/hikari-loop-2026-taipei",
    );
  });
});
