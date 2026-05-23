import { createFileRoute } from '@tanstack/react-router'
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { useAuth } from "@/hooks/use-auth"
import { User, Bell, Shield, Loader2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export const Route = createFileRoute("/_app/settings")({
  head: () => ({ meta: [{ title: "Settings — Team Nexus" }] }),
  component: SettingsPage,
})

function SettingsPage() {
  const { user } = useAuth()
  const [emailNotify, setEmailNotify] = useState(true)
  const [pushNotify, setPushNotify] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = () => {
    setIsSaving(true)
    setTimeout(() => {
      setIsSaving(false)
      toast.success("Settings saved successfully")
    }, 800)
  }

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete your account? This action is irreversible.")) {
      setIsSaving(true)
      try {
        const { deleteAccount } = await import("@/lib/api")
        await deleteAccount()
        toast.success("Account deleted successfully")
        // The auth hook doesn't expose logout directly here, so we clear token and reload
        const { tokenStorage } = await import("@/lib/api")
        tokenStorage.clear()
        window.location.href = "/login"
      } catch (err: any) {
        toast.error(err.message || "Failed to delete account")
      } finally {
        setIsSaving(false)
      }
    }
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage your account and application preferences.</p>
      </div>

      <div className="grid gap-8">
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground font-medium border-b border-border pb-2">
            <User className="h-4 w-4" /> Account Information
          </div>
          <Card className="p-6 rounded-2xl border border-border bg-card">
            <div className="grid gap-6 max-w-md">
              <div className="grid gap-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input id="full_name" defaultValue={user?.full_name} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" defaultValue={user?.email} disabled />
                <p className="text-[10px] text-muted-foreground">Email cannot be changed directly.</p>
              </div>
              <Button className="w-fit" onClick={handleSave} disabled={isSaving}>
                {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save changes"}
              </Button>
            </div>
          </Card>
        </section>

        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground font-medium border-b border-border pb-2">
            <Bell className="h-4 w-4" /> Notifications
          </div>
          <Card className="p-6 rounded-2xl border border-border bg-card">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Email Notifications</p>
                  <p className="text-xs text-muted-foreground">Receive daily summaries of your tasks.</p>
                </div>
                <Switch checked={emailNotify} onCheckedChange={setEmailNotify} />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Desktop Push</p>
                  <p className="text-xs text-muted-foreground">Get real-time alerts for @mentions.</p>
                </div>
                <Switch checked={pushNotify} onCheckedChange={setPushNotify} />
              </div>
            </div>
          </Card>
        </section>

        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground font-medium border-b border-border pb-2">
            <Shield className="h-4 w-4" /> Security
          </div>
          <Card className="p-6 rounded-2xl border border-border bg-card">
            <div className="flex flex-wrap gap-4">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline">Change Password</Button>
                </DialogTrigger>
                <DialogContent className="rounded-2xl">
                  <DialogHeader>
                    <DialogTitle>Change Password</DialogTitle>
                    <DialogDescription>Enter your current and new password below.</DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                      <Label>Current Password</Label>
                      <Input type="password" />
                    </div>
                    <div className="grid gap-2">
                      <Label>New Password</Label>
                      <Input type="password" />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={() => toast.success("Password updated")}>Update Password</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
              <Button variant="destructive" onClick={handleDelete}>Delete Account</Button>
            </div>
          </Card>
        </section>
      </div>
    </div>
  )
}
