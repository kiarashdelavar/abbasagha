"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ShieldCheck,
  ArrowRight,
  Lock,
  User,
  Key,
  CheckCircle2,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [step, setStep] = useState<
    "intro" | "connecting" | "oauth" | "verifying" | "success" | "introduction"
  >("intro");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleConnectClick = () => {
    setStep("connecting");
    setTimeout(() => {
      setStep("oauth");
    }, 1200);
  };

  const handleOAuthSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setStep("verifying");

    setTimeout(() => {
      setStep("success");

      setTimeout(() => {
        setStep("introduction");

        setTimeout(() => {
          router.push("/");
        }, 3600);
      }, 600);
    }, 2000);
  };

  return (
    <div className="min-h-screen w-full bg-black flex flex-col items-center justify-center p-4 font-sans relative overflow-hidden">
      {step === "introduction" && (
        <div className="fixed inset-0 z-[200] pointer-events-none">
          <div className="absolute inset-0 bg-black animate-intro-black-bg flex flex-col items-center justify-center">
            <div className="relative z-10 text-left animate-text-intro-sequence font-sans px-10">
              <h1 className="font-extrabold text-6xl md:text-8xl text-white tracking-tighter leading-[0.95]">
                Welcome to the
                <br />
                <span className="bunq-stripes-text">Abbas Agha</span>
              </h1>
              <p className="text-text/40 mt-4 text-xl font-medium tracking-wide">
                Initializing your AI Financial Copilot...
              </p>
            </div>
          </div>
          <div className="absolute inset-0 w-full h-full bunq-stripes-bg-horizontal animate-bunq-double-sweep z-20"></div>
        </div>
      )}

      <div className="absolute top-0 left-0 w-full h-1.5 bunq-stripes-bg-horizontal opacity-80"></div>

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-bunq-blue/5 rounded-full blur-[120px] pointer-events-none"></div>

      <div
        className={`w-full max-w-md bg-[#0a0a0a] border border-line-gray rounded-3xl p-8 shadow-2xl relative z-10 flex flex-col items-center text-center min-h-[460px] justify-center transition-all duration-500 ${step === "introduction" ? "opacity-0 scale-95" : "opacity-100 scale-100"}`}
      >
        {step === "intro" || step === "connecting" ? (
          <div className="flex flex-col items-center w-full animate-in fade-in zoom-in duration-300">
            <div className="w-20 h-20 rounded-2xl bg-[#111111] border border-line-gray/60 flex items-center justify-center mb-8 shadow-inner relative overflow-hidden">
              <div className="absolute inset-0 bunq-stripes-bg-vertical opacity-20"></div>
              <ShieldCheck size={40} className="text-white relative z-10" />
            </div>

            <h1 className="text-3xl font-extrabold text-white mb-2 tracking-tight">
              Welcome to <span className="bunq-stripes-text">ABASS AGHA</span>
            </h1>

            <p className="text-text/60 text-sm mb-10 leading-relaxed max-w-[280px]">
              Connect your bunq account securely to activate your AI Financial
              Copilot.
            </p>

            <button
              onClick={handleConnectClick}
              disabled={step === "connecting"}
              className="w-full bg-item-bg-offblack border border-line-gray relative group overflow-hidden rounded-2xl p-4 flex items-center justify-center gap-3 transition-all duration-300 btn-sweep-container"
            >
              <div className="sweep-layer"></div>

              <div className="relative z-10 flex items-center gap-3 text-white font-extrabold tracking-wide transition-colors duration-300">
                {step === "connecting" ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Connecting to bunq...
                  </>
                ) : (
                  <>
                    <Lock
                      size={18}
                      className="text-bunq-cyan group-hover:text-white transition-colors"
                    />
                    <span>Connect with bunq</span>
                    <ArrowRight
                      size={18}
                      className="text-white/70 group-hover:translate-x-1 group-hover:text-white transition-all"
                    />
                  </>
                )}
              </div>
            </button>

            <div className="mt-8 flex items-center justify-center gap-2 text-text/40 text-[11px] font-bold tracking-wider uppercase">
              <Lock size={12} />
              End-to-End Encrypted via OAuth 2.0
            </div>
          </div>
        ) : step === "oauth" || step === "verifying" || step === "success" ? (
          <form
            onSubmit={handleOAuthSubmit}
            className="flex flex-col items-center w-full animate-in slide-in-from-right-8 fade-in duration-500"
          >
            <h2 className="text-5xl font-extrabold tracking-tighter mb-8 bunq-stripes-text">
              bunq
            </h2>

            <div className="bg-[#111111] border border-line-gray/60 rounded-2xl p-4 w-full mb-6 text-left shadow-inner flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-item-bg-offblack border border-line-gray flex items-center justify-center flex-shrink-0">
                <ShieldCheck size={20} className="text-bunq-cyan" />
              </div>
              <div>
                <p className="text-white text-sm font-bold mb-1">ABASS AGHA</p>
                <p className="text-text/50 text-[11px] leading-relaxed">
                  Requests access to view your balance and initiate secure
                  transactions.
                </p>
              </div>
            </div>

            <div className="w-full space-y-3 mb-8">
              <div className="relative">
                <User
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-text/40"
                />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email or Phone Number"
                  className="w-full bg-[#111111] border border-line-gray/60 text-white p-4 pl-11 rounded-xl focus:outline-none focus:border-bunq-blue transition-colors text-[13px]"
                  disabled={step !== "oauth"}
                />
              </div>
              <div className="relative">
                <Key
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-text/40"
                />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="bunq Security Code"
                  className="w-full bg-[#111111] border border-line-gray/60 text-white p-4 pl-11 rounded-xl focus:outline-none focus:border-bunq-blue transition-colors text-[13px]"
                  disabled={step !== "oauth"}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={step !== "oauth"}
              className="w-full relative group overflow-hidden rounded-2xl p-4 flex items-center justify-center gap-3 transition-all duration-300"
              style={{
                background:
                  step === "success"
                    ? "var(--color-bunq-green)"
                    : "linear-gradient(135deg, var(--color-bunq-blue) 0%, var(--color-bunq-cyan) 100%)",
              }}
            >
              <div className="relative z-10 flex items-center gap-3 text-white font-extrabold tracking-wide">
                {step === "oauth" ? (
                  <>Authorize & Log In</>
                ) : step === "verifying" ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Verifying Credentials...
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={20} className="text-white" />
                    Successfully Connected
                  </>
                )}
              </div>
            </button>

            <button
              type="button"
              onClick={() => setStep("intro")}
              disabled={step !== "oauth"}
              className="mt-6 text-text/40 text-[12px] font-bold hover:text-white transition-colors"
            >
              Cancel and return
            </button>
          </form>
        ) : null}
      </div>

      <div className="mt-12 text-text/30 text-xs font-sans tracking-wide">
        © 2026 bunq. All rights reserved.
      </div>
    </div>
  );
}
