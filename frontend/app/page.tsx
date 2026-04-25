"use client";

import { useState, useRef, useEffect } from "react";
import {
  Search,
  Plus,
  Menu,
  X,
  MoreVertical,
  FileUp,
  Mic,
  SendHorizonal,
  Square,
  Trash2,
  Edit2,
  Pin,
  Paperclip,
  Play,
  Pause,
  LogOut,
} from "lucide-react";

export type Role = "user" | "ai" | "system";

export type OperationType =
  | "general_chat"
  | "arbitrage_scan"
  | "tax_report"
  | "receipt_analysis";

export interface Chat {
  id: number;
  title: string;
  isPinned: boolean;
  createdAt?: string;
}

export interface Attachment {
  id: string;
  type: "file" | "audio";
  url?: string;
  file?: File;
  fileName?: string;
  duration?: number;
}

export interface Message {
  id: string | number;
  role: Role;
  text: string;
  audioUrl?: string;
  fileName?: string;
  duration?: number;
  isLoading?: boolean;
  operationType?: OperationType;
  createdAt?: string;
  agentData?: any;
}

export interface ClaudePayload {
  chatId: number;
  operationType: OperationType;
  messages: {
    role: Role;
    content: string;
    attachments?: { type: string; name?: string; url?: string }[];
  };
  userContext?: {
    accountId: string;
    name: string;
  };
}

const mockUser = {
  firstName: "Mike",
  lastName: "Mortazavi",
  initial: "M",
  accountType: "bunq Easy Bank Pro • Active",
};

// آرایه‌های پیش‌فرض کاملاً خالی شدند تا صفحه تمیز لود شود
const initialChats: Chat[] = [];
const initialMessages: Message[] = [];

const bunqColors = [
  "var(--color-bunq-green)",
  "var(--color-bunq-lime)",
  "var(--color-bunq-cyan)",
  "var(--color-bunq-blue)",
  "var(--color-bunq-maroon)",
  "var(--color-bunq-red)",
  "var(--color-bunq-orange)",
  "var(--color-bunq-yellow)",
];

const CustomAudioPlayer = ({
  src,
  externalDuration,
}: {
  src: string;
  externalDuration?: number;
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  const staticHeights = [
    8, 14, 24, 12, 28, 16, 20, 32, 14, 26, 12, 18, 10, 16, 22, 12, 26, 14, 20,
    10, 18, 14, 24, 12,
  ];

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => {
      if (
        audio.duration &&
        audio.duration !== Infinity &&
        !isNaN(audio.duration)
      ) {
        setDuration(audio.duration);
      }
    };
    const onEnded = () => setIsPlaying(false);

    audio.addEventListener("timeupdate", updateTime);
    audio.addEventListener("loadedmetadata", updateDuration);
    audio.addEventListener("ended", onEnded);
    return () => {
      audio.removeEventListener("timeupdate", updateTime);
      audio.removeEventListener("loadedmetadata", updateDuration);
      audio.removeEventListener("ended", onEnded);
    };
  }, []);

  const displayDuration =
    (duration === Infinity || isNaN(duration) || duration === 0) &&
    externalDuration
      ? externalDuration
      : duration;

  const togglePlay = () => {
    if (isPlaying) audioRef.current?.pause();
    else audioRef.current?.play();
    setIsPlaying(!isPlaying);
  };

  const formatTime = (time: number) => {
    if (isNaN(time) || !isFinite(time)) return "0:00";
    const m = Math.floor(time / 60);
    const s = Math.floor(time % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex items-center gap-3 bg-[#111111] border border-line-gray/60 rounded-full p-1.5 px-4 w-max shadow-md">
      <audio ref={audioRef} src={src} className="hidden" />
      <button
        onClick={togglePlay}
        className="text-white hover:text-bunq-cyan transition flex-shrink-0"
      >
        {isPlaying ? (
          <Pause size={16} className="fill-current" />
        ) : (
          <Play size={16} className="fill-current" />
        )}
      </button>

      <div className="flex items-center gap-[2px] h-[24px]">
        {staticHeights.map((h, i) => {
          const progress = currentTime / (displayDuration || 1);
          const barProgress = i / staticHeights.length;
          const isActive = progress > barProgress;
          return (
            <div
              key={i}
              className="w-[3px] rounded-full transition-all duration-300"
              style={{
                height: `${isPlaying ? h : Math.max(4, h * 0.4)}px`,
                backgroundColor: bunqColors[i % 8],
                opacity: isActive || !isPlaying ? 1 : 0.3,
              }}
            />
          );
        })}
      </div>

      <span className="text-[#a0a0a0] font-medium text-[10px] tracking-wider font-sans ml-1 w-[60px] text-right">
        {formatTime(currentTime)} / {formatTime(displayDuration)}
      </span>
    </div>
  );
};

export default function Home() {
  const [chats, setChats] = useState<Chat[]>(initialChats);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isRevealing, setIsRevealing] = useState(false);

  const [activeChatId, setActiveChatId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [chatMessage, setChatMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>(initialMessages);

  const [contextMenu, setContextMenu] = useState<{
    id: number;
    x: number;
    y: number;
  } | null>(null);
  const [modal, setModal] = useState<{
    type: "rename" | "delete";
    id: number;
  } | null>(null);
  const [modalInput, setModalInput] = useState("");

  const [stagedFiles, setStagedFiles] = useState<
    { id: number; file: File; caption: string; progress: number | null }[]
  >([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedVoices, setRecordedVoices] = useState<
    { id: number; audioUrl: string; caption: string; duration: number }[]
  >([]);

  const [toast, setToast] = useState<{
    message: string;
    progress: number;
  } | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingStartTimeRef = useRef<number>(0);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const barsRef = useRef<(HTMLDivElement | null)[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (toast && toast.progress > 0) {
      interval = setInterval(() => {
        setToast((prev) => {
          if (!prev) return null;
          const newProg = prev.progress - 2;
          return newProg <= 0 ? null : { ...prev, progress: newProg };
        });
      }, 50);
    }
    return () => clearInterval(interval);
  }, [toast]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const showToast = (msg: string) => setToast({ message: msg, progress: 100 });

  const sortedChats = [...chats].sort(
    (a, b) => (b.isPinned ? 1 : 0) - (a.isPinned ? 1 : 0),
  );
  const filteredChats = sortedChats.filter((chat) =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleOpenSidebar = () => {
    setSidebarOpen(true);
    setIsRevealing(true);
    setTimeout(() => setIsRevealing(false), 400);
  };

  const handleContextMenu = (e: React.MouseEvent, chatId: number) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({ id: chatId, x: e.clientX, y: e.clientY });
  };

  const togglePinChat = (id: number) => {
    setChats(
      chats.map((c) => (c.id === id ? { ...c, isPinned: !c.isPinned } : c)),
    );
    setContextMenu(null);
  };

  const openRenameModal = (id: number) => {
    const chat = chats.find((c) => c.id === id);
    setModalInput(chat?.title || "");
    setModal({ type: "rename", id });
    setContextMenu(null);
  };

  const openDeleteModal = (id: number) => {
    setModal({ type: "delete", id });
    setContextMenu(null);
  };

  const handleModalConfirm = () => {
    if (!modal) return;
    if (modal.type === "rename") {
      if (modalInput.trim() !== "")
        setChats(
          chats.map((c) =>
            c.id === modal.id ? { ...c, title: modalInput } : c,
          ),
        );
    } else if (modal.type === "delete") {
      setChats(chats.filter((c) => c.id !== modal.id));
      if (activeChatId === modal.id) setActiveChatId(null);
    }
    setModal(null);
  };

  const handleLogout = () => {
    window.location.href = "/login";
  };

  const sendToBackend = async (
    payloadMsgs: Message[],
    targetChatId: number,
  ) => {
    const lastUserMessage =
      payloadMsgs.filter((m) => m.role === "user").pop()?.text ||
      "Sent an attachment";

    const tempAiId = Date.now() + "ai";
    setMessages((prev) => [
      ...prev,
      { id: tempAiId, role: "ai", text: "", isLoading: true },
    ]);

    try {
      const response = await fetch("http://localhost:8000/api/chat/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: "demo-user-1",
          message: lastUserMessage,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      setMessages((prev) =>
        prev.map((m) =>
          m.id === tempAiId
            ? {
                ...m,
                text: data.reply || "Processing complete.",
                isLoading: false,
                agentData: data.plan,
              }
            : m,
        ),
      );
    } catch (error) {
      console.error("Backend API Error:", error);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === tempAiId
            ? {
                ...m,
                text: "Error connecting to the A1 Copilot Backend. Check if FastAPI is running on 0.0.0.0",
                isLoading: false,
              }
            : m,
        ),
      );
    }
  };

  const handleSendMessage = () => {
    if (
      !chatMessage.trim() &&
      stagedFiles.length === 0 &&
      recordedVoices.length === 0
    )
      return;

    const newMessages: Message[] = [];
    const mainText = chatMessage.trim();

    stagedFiles.forEach((f) => {
      newMessages.push({
        id: Date.now() + Math.random(),
        role: "user",
        fileName: f.file.name,
        text: f.caption,
      });
    });

    recordedVoices.forEach((v) => {
      newMessages.push({
        id: Date.now() + Math.random(),
        role: "user",
        audioUrl: v.audioUrl,
        duration: v.duration,
        text: v.caption,
      });
    });

    if (mainText || newMessages.length === 0) {
      if (newMessages.length > 0) {
        newMessages[newMessages.length - 1].text = newMessages[
          newMessages.length - 1
        ].text
          ? `${newMessages[newMessages.length - 1].text}\n\n${mainText}`
          : mainText;
      } else {
        newMessages.push({
          id: Date.now() + Math.random(),
          role: "user",
          text: mainText,
        });
      }
    }

    // Auto-create chat if none is active
    let currentChatId = activeChatId;
    let isNewChat = false;

    if (!currentChatId) {
      currentChatId = Date.now();
      isNewChat = true;
      const newChatTitle = mainText
        ? mainText.substring(0, 20) + "..."
        : "New Chat";
      setChats((prev) => [
        { id: currentChatId, title: newChatTitle, isPinned: false },
        ...prev,
      ]);
      setActiveChatId(currentChatId);
    }

    if (isNewChat) {
      setMessages(newMessages); // Fresh start for new chat
    } else {
      setMessages((prev) => [...prev, ...newMessages]); // Append to existing
    }

    setChatMessage("");
    setStagedFiles([]);
    setRecordedVoices([]);

    sendToBackend(newMessages, currentChatId);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const existingFileNames = stagedFiles.map((f) => f.file.name);

    Array.from(files).forEach((file) => {
      if (existingFileNames.includes(file.name)) {
        showToast(`File "${file.name}" is already attached!`);
        return;
      }

      const fileId = Date.now() + Math.random();
      setStagedFiles((prev) => [
        ...prev,
        { id: fileId, file, caption: "", progress: 0 },
      ]);

      const interval = setInterval(() => {
        setStagedFiles((prev) => {
          return prev.map((f) => {
            if (f.id === fileId) {
              if (f.progress !== null && f.progress >= 100) {
                clearInterval(interval);
                return { ...f, progress: 100 };
              }
              return { ...f, progress: (f.progress || 0) + 20 };
            }
            return f;
          });
        });
      }, 150);
    });

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removeStagedFile = (id: number) =>
    setStagedFiles((prev) => prev.filter((f) => f.id !== id));
  const updateFileCaption = (id: number, caption: string) =>
    setStagedFiles((prev) =>
      prev.map((f) => (f.id === id ? { ...f, caption } : f)),
    );
  const removeRecordedVoice = (id: number) =>
    setRecordedVoices((prev) => prev.filter((v) => v.id !== id));
  const updateVoiceCaption = (id: number, caption: string) =>
    setRecordedVoices((prev) =>
      prev.map((v) => (v.id === id ? { ...v, caption } : v)),
    );

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsRecording(true);
      audioChunksRef.current = [];
      recordingStartTimeRef.current = Date.now();
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm",
          });
          const audioUrl = URL.createObjectURL(audioBlob);
          const durationInSeconds =
            (Date.now() - recordingStartTimeRef.current) / 1000;
          setRecordedVoices((prev) => [
            ...prev,
            {
              id: Date.now(),
              audioUrl,
              caption: "",
              duration: durationInSeconds,
            },
          ]);
        }
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start(200);

      const audioCtx = new (
        window.AudioContext || (window as any).webkitAudioContext
      )();
      const analyser = audioCtx.createAnalyser();
      analyserRef.current = analyser;
      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 64;
      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const updateVisualizer = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        for (let i = 0; i < 24; i++) {
          if (barsRef.current[i]) {
            const height = Math.max(4, (dataArray[i] / 255) * 35);
            barsRef.current[i]!.style.height = `${height}px`;
          }
        }
        animationFrameRef.current = requestAnimationFrame(updateVisualizer);
      };
      updateVisualizer();
    } catch (error) {
      alert("Microphone access denied.");
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === "recording"
    )
      mediaRecorderRef.current.stop();
    if (animationFrameRef.current)
      cancelAnimationFrame(animationFrameRef.current);
  };

  const cancelRecording = () => {
    setIsRecording(false);
    audioChunksRef.current = [];
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === "recording"
    )
      mediaRecorderRef.current.stop();
    if (animationFrameRef.current)
      cancelAnimationFrame(animationFrameRef.current);
  };

  return (
    <div
      className="flex h-screen w-full overflow-hidden text-sm relative"
      onClick={() => setContextMenu(null)}
    >
      <aside
        className={`bg-black flex flex-col transition-all duration-700 ease-in-out relative ${sidebarOpen ? "w-80 border-r border-line-gray" : "w-0 overflow-hidden"}`}
      >
        <div
          className={`absolute top-0 right-0 h-full bunq-stripes-bg-vertical transition-all ease-in-out z-50 ${sidebarOpen ? (isRevealing ? "w-full duration-300" : "w-1 duration-700") : "w-0 duration-200"}`}
        />

        <div className="relative z-30 flex flex-col h-full w-80">
          <div className="p-4 border-b border-line-gray flex items-center h-[69px] relative z-40 bg-black">
            <div className="flex-1 flex items-center gap-2 overflow-hidden relative z-30">
              <X
                size={20}
                className="text-text/60 cursor-pointer hover:text-white transition"
                onClick={() => setSidebarOpen(false)}
              />
              <span className="font-extrabold text-lg text-white truncate px-2 font-sans tracking-wide">
                What's going on?
              </span>
            </div>
          </div>

          <div className="p-4">
            <button
              onClick={() => {
                setActiveChatId(null);
                setMessages([]);
              }}
              className="w-full flex items-center justify-center gap-2 bg-item-bg-offblack text-text font-bold p-3 rounded-xl transition duration-200 border border-line-gray btn-sweep-container group font-sans"
            >
              <div className="sweep-layer opacity-40"></div>
              <Plus size={18} className="relative z-10" />{" "}
              <span className="relative z-10">New Chat</span>
            </button>
          </div>

          <div className="px-4 pb-4 border-b border-line-gray relative z-30">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search chats by keyword..."
                className="w-full bg-item-bg-offblack text-text p-3 pl-10 rounded-xl focus:outline-none focus:ring-2 focus:ring-bunq-cyan/50 transition border border-line-gray placeholder:text-text/30 font-sans"
              />
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-text/40"
                size={18}
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2 relative z-30">
            {filteredChats.map((chat) => (
              <div
                key={chat.id}
                className={`flex items-center justify-between p-3 rounded-xl transition cursor-pointer border ${activeChatId === chat.id ? "bg-item-bg-offblack border-line-gray" : "hover:bg-item-bg-offblack border-transparent"}`}
                onClick={() => {
                  setActiveChatId(chat.id);
                }}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  {chat.isPinned && (
                    <Pin size={12} className="text-bunq-cyan flex-shrink-0" />
                  )}
                  <span className="text-text/80 truncate font-sans text-[13px]">
                    {chat.title}
                  </span>
                </div>
                <button
                  onClick={(e) => handleContextMenu(e, chat.id)}
                  className="text-text/30 hover:text-text/100 p-1 rounded-md transition flex-shrink-0"
                >
                  <MoreVertical size={16} />
                </button>
              </div>
            ))}
          </div>

          <div className="p-4 border-t border-line-gray mt-auto bg-black relative z-30">
            <div className="flex items-center gap-3 p-2 rounded-2xl bg-item-bg-offblack border border-line-gray/50 group relative">
              <div className="w-10 h-10 rounded-full flex-shrink-0 p-[2px] bunq-stripes-bg-horizontal">
                <div className="w-full h-full bg-[#111111] rounded-full flex items-center justify-center font-extrabold text-white text-lg">
                  {mockUser.initial}
                </div>
              </div>

              <div className="flex-1 overflow-hidden">
                <div className="text-white font-bold text-[13px] truncate font-sans">
                  {mockUser.firstName} {mockUser.lastName}
                </div>
                <div className="text-text/40 text-[10px] truncate font-sans tracking-tight mt-0.5">
                  {mockUser.accountType}
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="p-2 rounded-xl text-text/40 hover:text-bunq-red hover:bg-bunq-red/10 transition flex-shrink-0"
                title="Log out"
              >
                <LogOut size={16} />
              </button>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col bg-black relative min-w-0">
        {toast && (
          <div className="absolute top-6 left-1/2 transform -translate-x-1/2 z-[150] bg-item-bg-offblack border border-line-gray rounded-xl p-4 shadow-2xl flex flex-col gap-3 min-w-[320px] max-w-[90%] font-sans">
            <div className="flex justify-between items-center gap-4">
              <span className="text-white text-[13px] font-bold">
                {toast.message}
              </span>
              <button onClick={() => setToast(null)}>
                <X
                  size={16}
                  className="text-text/40 hover:text-white transition"
                />
              </button>
            </div>
            <div className="w-full h-1.5 bg-black rounded-full overflow-hidden mt-1">
              <div
                className="h-full bunq-stripes-bg-horizontal transition-all duration-75 ease-linear"
                style={{ width: `${toast.progress}%` }}
              ></div>
            </div>
          </div>
        )}

        <header className="p-4 border-b border-line-gray flex items-center bg-black z-10 relative h-[69px]">
          <div className="flex-1 flex items-center gap-4 relative z-30">
            {!sidebarOpen && (
              <button
                onClick={handleOpenSidebar}
                className="text-text/60 hover:text-text"
              >
                <Menu size={24} />
              </button>
            )}
            <span className="font-extrabold text-lg bunq-stripes-text tracking-wider whitespace-nowrap hidden sm:block">
              ABASS AGHA
            </span>
          </div>

          <div className="absolute left-1/2 transform -translate-x-1/2 w-full max-w-sm pointer-events-none text-center z-20">
            <h1 className="font-extrabold text-base text-white truncate px-4 font-sans tracking-wide">
              {activeChatId
                ? chats.find((c) => c.id === activeChatId)?.title
                : ""}
            </h1>
          </div>
          <div className="flex-1 relative z-30"></div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeChatId ? (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`flex flex-col gap-2 max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"}`}
                >
                  {msg.role === "ai" && (
                    <div className="font-bold bunq-stripes-text tracking-wide mb-1 px-2 bg-black border border-line-gray rounded-full p-1.5 w-max">
                      ABASS AGHA
                    </div>
                  )}

                  {msg.audioUrl && (
                    <CustomAudioPlayer
                      src={msg.audioUrl}
                      externalDuration={msg.duration}
                    />
                  )}

                  {msg.fileName && (
                    <div className="bg-[#111111] border border-line-gray/60 rounded-xl p-3 flex items-center gap-3 text-white shadow-md w-max">
                      <Paperclip size={18} className="text-bunq-cyan" />
                      <span className="font-sans text-[13px] truncate">
                        {msg.fileName}
                      </span>
                    </div>
                  )}

                  {msg.text && (
                    <div className="bg-[#111111] text-text/90 p-4 rounded-2xl font-sans leading-relaxed border border-line-gray/60 shadow-md flex items-center gap-2">
                      <div dir="auto" className="whitespace-pre-wrap">
                        {msg.text}
                      </div>
                      {msg.isLoading && (
                        <div className="flex gap-1 items-center justify-center ml-2">
                          <div
                            className="w-1.5 h-1.5 rounded-full bg-bunq-cyan animate-bounce"
                            style={{ animationDelay: "0ms" }}
                          ></div>
                          <div
                            className="w-1.5 h-1.5 rounded-full bg-bunq-blue animate-bounce"
                            style={{ animationDelay: "150ms" }}
                          ></div>
                          <div
                            className="w-1.5 h-1.5 rounded-full bg-bunq-maroon animate-bounce"
                            style={{ animationDelay: "300ms" }}
                          ></div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-3">
              <h2 className="text-4xl font-extrabold text-text font-sans">
                Hey{" "}
                <span className="bunq-stripes-text">{mockUser.firstName}</span>,
              </h2>
              <p className="text-xl text-text/60 font-sans">
                how can I help you?
              </p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <footer className="p-4 pt-3 border-t border-line-gray bg-black z-10 relative">
          <div className="max-w-4xl mx-auto w-full flex flex-col gap-3">
            {(stagedFiles.length > 0 || recordedVoices.length > 0) && (
              <div className="flex flex-col gap-2 w-full">
                {recordedVoices.length > 0 && (
                  <div className="flex flex-wrap gap-3 w-full">
                    {recordedVoices.map((v) => (
                      <div key={v.id} className="flex items-center gap-2">
                        <CustomAudioPlayer
                          src={v.audioUrl}
                          externalDuration={v.duration}
                        />
                        <button
                          onClick={() => removeRecordedVoice(v.id)}
                          className="p-2 text-bunq-red hover:bg-bunq-red/15 rounded-full transition flex-shrink-0"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {stagedFiles.map((f) => (
                  <div key={f.id} className="flex items-center gap-3">
                    <div className="flex-1 bg-[#111111] border border-line-gray/60 rounded-xl p-3 px-4 flex items-center gap-3 shadow-md">
                      <Paperclip
                        size={18}
                        className="text-bunq-cyan flex-shrink-0"
                      />
                      <span className="text-white text-[13px] truncate font-sans">
                        {f.file.name}
                      </span>
                      {f.progress !== null && f.progress < 100 && (
                        <div className="ml-auto w-24 h-1.5 bg-black rounded-full overflow-hidden flex-shrink-0">
                          <div
                            className="h-full bunq-stripes-bg-horizontal transition-all duration-200"
                            style={{ width: `${f.progress}%` }}
                          ></div>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => removeStagedFile(f.id)}
                      className="p-2.5 text-bunq-red hover:bg-bunq-red/15 rounded-xl transition flex-shrink-0"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-end gap-3 bg-item-bg-offblack p-2 rounded-2xl border border-line-gray relative">
              <input
                type="file"
                multiple
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileChange}
              />

              <div
                className={`relative group w-[38px] h-[38px] flex items-center justify-center rounded-xl transition mb-1 ${!isRecording ? "hover:bg-line-gray cursor-pointer" : "opacity-50 cursor-not-allowed"}`}
                onClick={() => !isRecording && fileInputRef.current?.click()}
              >
                <FileUp
                  size={18}
                  className="text-text/40 transition-opacity group-hover:opacity-0"
                />
                <div
                  className="absolute inset-0 m-auto w-[18px] h-[18px] opacity-0 transition-opacity pointer-events-none group-hover:opacity-100"
                  style={{
                    background: `linear-gradient(to right, var(--color-bunq-green), var(--color-bunq-lime), var(--color-bunq-green))`,
                    backgroundSize: "200% 100%",
                    animation: "wave-animation 1s linear infinite",
                    WebkitMask: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z'/%3E%3Cpath d='M14 2v4a2 2 0 0 0 2 2h4'/%3E%3Cpath d='M12 12v6'/%3E%3Cpath d='m15 15-3-3-3 3'/%3E%3C/svg%3E") center/contain no-repeat`,
                    mask: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z'/%3E%3Cpath d='M14 2v4a2 2 0 0 0 2 2h4'/%3E%3Cpath d='M12 12v6'/%3E%3Cpath d='m15 15-3-3-3 3'/%3E%3C/svg%3E") center/contain no-repeat`,
                  }}
                ></div>
              </div>

              <div className="flex-1 min-h-[46px] flex items-center justify-center">
                {isRecording ? (
                  <div className="flex items-center gap-3 w-full px-2">
                    <div className="flex items-center gap-2 text-text/60 font-bold font-sans">
                      <div className="w-2.5 h-2.5 rounded-full bg-bunq-red animate-pulse"></div>
                      Recording...
                    </div>
                    <div className="flex items-end gap-[2px] h-[30px] flex-1">
                      {Array.from({ length: 24 }).map((_, i) => (
                        <div
                          key={i}
                          ref={(el) => {
                            barsRef.current[i] = el;
                          }}
                          className="w-[3px] rounded-full min-h-[4px] transition-all duration-75"
                          style={{ backgroundColor: bunqColors[i % 8] }}
                        />
                      ))}
                    </div>
                  </div>
                ) : (
                  <textarea
                    dir="auto"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={
                      stagedFiles.length > 0 || recordedVoices.length > 0
                        ? "Add a caption..."
                        : "Ask ABASS AGHA..."
                    }
                    className="w-full bg-transparent text-text p-2 mt-1 max-h-[150px] resize-none focus:outline-none font-sans text-[13px] overflow-y-auto placeholder:text-text/30 leading-relaxed"
                    rows={1}
                  />
                )}
              </div>

              {isRecording ? (
                <div className="flex items-center gap-1 mb-1">
                  <button
                    onClick={cancelRecording}
                    className="p-2.5 rounded-xl text-bunq-red hover:bg-bunq-red/15 transition"
                  >
                    <Trash2 size={18} />
                  </button>
                  <button
                    onClick={stopRecording}
                    className="p-2.5 rounded-xl bg-line-gray text-white hover:bg-[#5a5a5a] transition"
                  >
                    <Square size={18} className="fill-current" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={startRecording}
                  className="p-2.5 rounded-xl text-text/40 hover:text-text hover:bg-line-gray transition mb-1"
                  disabled={stagedFiles.length > 0 || recordedVoices.length > 0}
                >
                  <Mic size={18} />
                </button>
              )}

              <div
                className={`relative group w-[38px] h-[38px] flex items-center justify-center rounded-xl transition mb-1 ${(chatMessage.trim() || stagedFiles.length > 0 || recordedVoices.length > 0) && !isRecording ? "hover:bg-line-gray cursor-pointer" : "opacity-50 cursor-not-allowed"}`}
                onClick={!isRecording ? handleSendMessage : undefined}
              >
                <SendHorizonal
                  size={18}
                  className={`text-text/40 transition-opacity ${chatMessage.trim() || stagedFiles.length > 0 || recordedVoices.length > 0 ? "group-hover:opacity-0" : ""}`}
                />
                <div
                  className={`absolute inset-0 m-auto w-[18px] h-[18px] opacity-0 transition-opacity bunq-stripes-wave pointer-events-none ${chatMessage.trim() || stagedFiles.length > 0 || recordedVoices.length > 0 ? "group-hover:opacity-100" : ""}`}
                  style={{
                    WebkitMask: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3.714 3.048a.498.498 0 0 0-.683.627l2.843 7.627a2 2 0 0 1 0 1.396l-2.843 7.627a.498.498 0 0 0 .683.627l18-8.5a.5.5 0 0 0 0-.904z'/%3E%3Cpath d='M6 12h16'/%3E%3C/svg%3E") center/contain no-repeat`,
                    mask: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3.714 3.048a.498.498 0 0 0-.683.627l2.843 7.627a2 2 0 0 1 0 1.396l-2.843 7.627a.498.498 0 0 0 .683.627l18-8.5a.5.5 0 0 0 0-.904z'/%3E%3Cpath d='M6 12h16'/%3E%3C/svg%3E") center/contain no-repeat`,
                  }}
                ></div>
              </div>
            </div>
          </div>
          <div className="text-center text-text/30 text-[10px] mt-3 font-sans tracking-wide">
            © 2026 bunq. All rights reserved.
          </div>
        </footer>
      </main>

      {contextMenu && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/20"
            onClick={() => setContextMenu(null)}
          ></div>
          <div
            className="fixed z-50 bg-item-bg-offblack border border-line-gray rounded-xl shadow-2xl p-1.5 w-48 font-sans overflow-hidden"
            style={{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => togglePinChat(contextMenu.id)}
              className="w-full flex items-center gap-3 text-left p-2.5 rounded-lg hover:bg-line-gray transition text-[13px] text-text/90"
            >
              <Pin size={14} className="text-text/60" />{" "}
              {chats.find((c) => c.id === contextMenu.id)?.isPinned
                ? "Unpin Chat"
                : "Pin Chat"}
            </button>
            <button
              onClick={() => openRenameModal(contextMenu.id)}
              className="w-full flex items-center gap-3 text-left p-2.5 rounded-lg hover:bg-line-gray transition text-[13px] text-text/90"
            >
              <Edit2 size={14} className="text-text/60" /> Rename
            </button>
            <div className="h-px bg-line-gray my-1 mx-2"></div>
            <button
              onClick={() => openDeleteModal(contextMenu.id)}
              className="w-full flex items-center gap-3 text-left p-2.5 rounded-lg hover:bg-line-gray transition text-[13px] text-bunq-red group"
            >
              <Trash2
                size={14}
                className="text-bunq-red/70 group-hover:text-bunq-red"
              />{" "}
              Delete
            </button>
          </div>
        </>
      )}

      {modal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 font-sans leading-auto">
          <div className="bg-item-bg-offblack border border-line-gray rounded-2xl p-6 w-full max-w-md shadow-2xl transform transition-all relative z-10">
            <h3 className="text-xl font-extrabold text-white mb-4 tracking-tight">
              {modal.type === "rename" ? "Rename Chat" : "Delete Chat"}
            </h3>
            {modal.type === "rename" ? (
              <input
                type="text"
                value={modalInput}
                onChange={(e) => setModalInput(e.target.value)}
                className="w-full bg-black text-white p-3 rounded-xl border border-line-gray focus:outline-none focus:border-bunq-blue transition font-sans"
                placeholder="Enter chat name..."
                autoFocus
                dir="auto"
              />
            ) : (
              <p className="text-text/70 text-sm font-sans leading-relaxed">
                Are you sure you want to permanently delete this chat? This
                action cannot be undone.
              </p>
            )}
            <div className="flex gap-3 mt-8">
              <button
                onClick={() => setModal(null)}
                className="flex-1 p-3 rounded-xl border border-line-gray text-text/70 hover:text-bunq-red hover:bg-bunq-red/10 hover:border-bunq-red transition duration-200 font-bold font-sans"
              >
                Cancel
              </button>
              <button
                onClick={handleModalConfirm}
                className="flex-1 p-3 rounded-xl border border-line-gray text-white font-bold btn-sweep-container group overflow-hidden font-sans"
              >
                <div className="sweep-layer"></div>
                <span className="relative z-10 group-hover:text-white transition-colors duration-300">
                  {modal.type === "rename" ? "Save" : "Yes, Delete"}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
