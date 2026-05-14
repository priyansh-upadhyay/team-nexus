import { createFileRoute, useNavigate, Link } from '@tanstack/react-router'
import { useState } from "react";
import { Shield, Loader2 } from "lucide-react";
import { ApiError, register } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/register")({
  head: () => ({ meta: [{ title: "Create account — Team Nexus" }] }),
  component: RegisterPage,
});

function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    setError(null);
    setLoading(true);
    try {
      const res = await register(email, fullName, password);
      if (!res?.access_token) throw new Error("Missing access token in response");
      await login(res.access_token);
      navigate({ to: "/dashboard" });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message || "Registration failed. Please check your details.");
      } else {
        setError("Network error. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="px-6 sm:px-10 py-6 flex items-center gap-2">
        <div className="h-7 w-7 rounded-lg flex items-center justify-center bg-primary text-primary-foreground shadow-sm">
          <Shield className="h-3.5 w-3.5" />
        </div>
        <span className="font-semibold tracking-tight text-foreground">Team Nexus</span>
      </header>

      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 pb-16">
        <div className="w-full max-w-[400px]">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">Create your account</h1>
            <p className="text-sm text-muted-foreground mt-2">
              Start collaborating with your team in minutes.
            </p>
          </div>

          <div className="glass rounded-2xl p-7 sm:p-8 border border-border shadow-sm">
            <form className="space-y-5" onSubmit={handleSubmit} noValidate>
              <div className="space-y-1.5">
                <Label htmlFor="name" className="text-xs font-medium text-muted-foreground">
                  Full name
                </Label>
                <Input 
                  id="name" 
                  type="text" 
                  placeholder="Alex Morgan" 
                  className="h-10" 
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="email" className="text-xs font-medium text-muted-foreground">
                  Work email
                </Label>
                <Input 
                  id="email" 
                  type="email" 
                  placeholder="you@company.com" 
                  className="h-10" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="password" className="text-xs font-medium text-muted-foreground">
                  Password
                </Label>
                <Input 
                  id="password" 
                  type="password" 
                  placeholder="At least 8 characters" 
                  className="h-10" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>

              {error && (
                <div role="alert" className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md px-3 py-2">
                  {error}
                </div>
              )}

              <Button type="submit" className="w-full h-10 font-medium" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Creating account…
                  </>
                ) : (
                  "Create account"
                )}
              </Button>

              <p className="text-[11px] text-muted-foreground text-center leading-relaxed">
                By creating an account, you agree to our{" "}
                <a className="underline hover:text-foreground cursor-pointer">Terms</a> and{" "}
                <a className="underline hover:text-foreground cursor-pointer">Privacy Policy</a>.
              </p>
            </form>
          </div>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-foreground font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
