const focusRoot = document.documentElement;

// Native :focus-visible can match editable fields after a pointer interaction.
document.addEventListener("pointerdown", () => {
  focusRoot.dataset.focusInput = "pointer";
}, { capture: true, passive: true });

document.addEventListener("keydown", (event) => {
  if (["Alt", "Control", "Meta", "Shift"].includes(event.key)) return;
  delete focusRoot.dataset.focusInput;
}, { capture: true });
