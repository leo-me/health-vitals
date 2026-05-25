"use client";

import { useState } from "react";
import { ActivityIcon, Loader2 } from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { loginRequest } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/authStore";
import { extractDetail } from "@/lib/api/errors";


export function LoginModal() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const login = useAuthStore((s) => s.login);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      const { access_token } = await loginRequest(email, password);
      login(access_token);
      toast.success("Signed in.");
    } catch (err) {
      toast.error(extractDetail(err));
    } finally {
      setSubmitting(false);

    }
  }

  console.log(9999);


  return (
    <Dialog
      open
      // Non-dismissible: ignore Esc / outside-click attempts.
      onOpenChange={() => {
        /* no-op */
      }}
      // Belt-and-suspenders — block outside-click at the source too.
    >

      <DialogContent showCloseButton={false} className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-lg bg-vital flex items-center justify-center">
              <ActivityIcon className="w-4 h-4 text-vital-foreground" />
            </div>
            <span className="font-heading font-bold tracking-tight">Sensors2Care</span>
          </div>
          <DialogTitle>Sign in to the admin console</DialogTitle>
          <DialogDescription>
            Use the email and password registered with the backend.
          </DialogDescription>
        </DialogHeader>

        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label htmlFor="login-email">Email</Label>
            <Input
              id="login-email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={submitting}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="login-password">Password</Label>
            <Input
              id="login-password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting}
            />
          </div>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Signing in…
              </>
            ) : (
              "Sign in"
            )}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
