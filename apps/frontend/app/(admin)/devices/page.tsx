"use client";

import { useState } from "react";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/layout/PageHeader";
import { UUIDCell } from "@/components/common/UUIDCell";
import { TimestampCell } from "@/components/common/TimestampCell";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDevices } from "@/hooks/useDevices";
import { deleteDevice } from "@/lib/api/endpoints";
import { extractDetail } from "@/lib/api/errors";
import type { DeviceResponse } from "@/types/backend";
import { DeviceFormDialog } from "./_components/DeviceFormDialog";

export default function DevicesPage() {
  const devices = useDevices();
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<DeviceResponse | null>(null);
  const [confirmingDelete, setConfirmingDelete] = useState<DeviceResponse | null>(null);
  const [deletingPending, setDeletingPending] = useState(false);

  async function doDelete() {
    if (!confirmingDelete) return;
    setDeletingPending(true);
    try {
      await deleteDevice(confirmingDelete.id);
      toast.success("Device deleted.");
      setConfirmingDelete(null);
      await devices.refetch();
    } catch (err) {
      toast.error(extractDetail(err));
    } finally {
      setDeletingPending(false);
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <PageHeader
        title="Devices"
        description="Manage the wearables and sensors registered to your account."
        actions={
          <Button
            onClick={() => {
              setEditing(null);
              setFormOpen(true);
            }}
          >
            <Plus className="w-4 h-4 mr-1" /> Add device
          </Button>
        }
      />

      <div className="bg-card border rounded-lg shadow-sm overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Device ID</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Serial</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-32 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {devices.loading && devices.data === undefined ? (
              [0, 1, 2].map((i) => (
                <TableRow key={i}>
                  <TableCell colSpan={5}>
                    <Skeleton className="h-8 w-full" />
                  </TableCell>
                </TableRow>
              ))
            ) : devices.data && devices.data.length > 0 ? (
              devices.data.map((d) => (
                <TableRow key={d.id} className="hover:bg-muted/40">
                  <TableCell>
                    <UUIDCell value={d.id} />
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="capitalize">
                      {d.type}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {d.serial_number ?? <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    <TimestampCell value={d.created_at} />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="inline-flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditing(d);
                          setFormOpen(true);
                        }}
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setConfirmingDelete(d)}
                      >
                        <Trash2 className="w-4 h-4 text-danger" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground py-12">
                  No devices yet. Click <strong>Add device</strong> to register one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <DeviceFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        initial={editing}
        onSaved={() => devices.refetch()}
      />
      <ConfirmDialog
        open={!!confirmingDelete}
        onOpenChange={(o) => !o && setConfirmingDelete(null)}
        title="Delete device?"
        description={
          confirmingDelete
            ? `Device ${confirmingDelete.id.slice(0, 8)}… will be permanently removed.`
            : ""
        }
        destructive
        confirmLabel="Delete"
        loading={deletingPending}
        onConfirm={doDelete}
      />
    </div>
  );
}
