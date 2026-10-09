import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    primary: { main: "#0067b8" },
    secondary: { main: "#5c2d91" },
    background: { default: "#f5f7fa" },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif',
    h1: { fontSize: "clamp(2rem, 5vw, 3.25rem)", fontWeight: 700 },
    h2: { fontSize: "clamp(1.5rem, 3vw, 2rem)", fontWeight: 700 },
  },
  components: {
    MuiButton: { defaultProps: { disableElevation: true } },
  },
});
