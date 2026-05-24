"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DEVICE_TYPES, type DeviceResponse, type DeviceType } from "@/types/backend";
import { createDevice, updateDevice } from "@/lib/api/endpoints";
import { extractDetail } from "@/lib/api/errors";

interface DeviceFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initial?: DeviceResponse | null;
  onSaved: () => void;
}

export function DeviceFormDialog({
  open,
  onOpenChange,
  initial,
  onSaved,
}: DeviceFormDialogProps) {
  const editing = !!initial;
  const [type, setType] = useState<DeviceType>("watch");
  const [serial, setSerial] = useState("");
  const [pushToken, setPushToken] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      // Reset form to match the device being edited (or defaults for create).
      // React 19 lint flags setState-in-effect here, but resetting derived form
      // state when the dialog opens is the canonical pattern.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setType(initial?.type ?? "watch");
      setSerial(initial?.serial_number ?? "");
      setPushToken("");
    }
  }, [open, initial]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      if (editing && initial) {
        await updateDevice(initial.id, {
          type,
          serial_number: serial || undefined,
          push_token: pushToken || undefined,
        });
        toast.success("Device updated.");
      } else {
        await createDevice({
          type,
          serial_number: serial || undefined,
          push_token: pushToken || undefined,
        });
        toast.success("Device created.");
      }
      onSaved();
      onOpenChange(false);
    } catch (err) {
      toast.error(extractDetail(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{editing ? "Edit device" : "Add device"}</DialogTitle>
          <DialogDescription>
            {editing
              ? "Update the device's type or serial number."
              : "Register a new device for the signed-in user."}
          </DialogDescription>
        </DialogHeader>

        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label htmlFor="device-type">Type</Label>
            <Select value={type} onValueChange={(v) => setType(v as DeviceType)}>
              <SelectTrigger id="device-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DEVICE_TYPES.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="device-serial">Serial number</Label>
            <Input
              id="device-serial"
              value={serial}
              onChange={(e) => setSerial(e.target.value)}
              placeholder="e.g. E4-04-2B-12-34-56"
              disabled={submitting}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="device-push">Push token (optional)</Label>
            <Input
              id="device-push"
              value={pushToken}
              onChange={(e) => setPushToken(e.target.value)}
              placeholder="APNs / FCM token"
              disabled={submitting}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              {editing ? "Save changes" : "Create device"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
