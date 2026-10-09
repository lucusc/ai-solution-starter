import AccountCircleOutlined from "@mui/icons-material/AccountCircleOutlined";
import AutoAwesomeOutlined from "@mui/icons-material/AutoAwesomeOutlined";
import LoginOutlined from "@mui/icons-material/LoginOutlined";
import LogoutOutlined from "@mui/icons-material/LogoutOutlined";
import {
  AppBar,
  Box,
  Button,
  Chip,
  Container,
  Link,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { Link as RouterLink, Outlet } from "react-router-dom";

import {
  getAccount,
  signInUrl,
  signOutUrl,
  type Account,
} from "../api/auth";

export function AppShell() {
  const [account, setAccount] = useState<Account | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void getAccount(controller.signal).then(setAccount).catch(() => undefined);
    return () => controller.abort();
  }, []);

  return (
    <Box minHeight="100vh">
      <AppBar position="static" color="inherit" elevation={0}>
        <Toolbar>
          <Link
            component={RouterLink}
            to="/"
            color="inherit"
            underline="none"
            sx={{ display: "flex", alignItems: "center", gap: 1 }}
          >
            <AutoAwesomeOutlined color="primary" />
            <Typography component="span" fontWeight={700}>
              AI Solution Starter
            </Typography>
          </Link>
          <Box flexGrow={1} />
          {account ? (
            <Stack direction="row" alignItems="center" gap={1}>
              <Chip
                icon={<AccountCircleOutlined />}
                label={account.displayName}
                variant="outlined"
              />
              {!account.isLocal && (
                <Button
                  component="a"
                  href={signOutUrl}
                  color="inherit"
                  startIcon={<LogoutOutlined />}
                >
                  Sign out
                </Button>
              )}
            </Stack>
          ) : (
            <Button
              component="a"
              href={signInUrl}
              color="inherit"
              startIcon={<LoginOutlined />}
            >
              Sign in
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Container component="main" maxWidth="lg" sx={{ py: { xs: 3, md: 5 } }}>
        <Outlet />
      </Container>
    </Box>
  );
}
