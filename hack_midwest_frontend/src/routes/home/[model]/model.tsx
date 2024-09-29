import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { getModel, filePost } from "./requests";
import { projects } from "@/db/db";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { FaFileAlt } from "react-icons/fa";
import { GoPaperclip } from "react-icons/go";
import { IoIosSend } from "react-icons/io";
import { AiOutlineLoading } from "react-icons/ai";
import { useToast } from "@/hooks/use-toast";
import { Toaster } from "@/components/ui/toaster";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function ModelDashboard() {
  const { toast } = useToast();
  const [messages, setMessages] = useState<{}[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  console.log(files);
  const queryClient = useQueryClient();
  const { id } = useParams();
  const { register, handleSubmit } = useForm();

  const { data, isPending } = useQuery({
    queryKey: ["model", id],
    queryFn: getModel,
  });
  const { mutate, isPending: mutatePending } = useMutation({
    mutationFn: filePost,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["model", id] });
      console.log("filePost success!");
    },
    onError: () => {
      toast({
        title: "Something went wrong...",
        className: "bg-red-200",
      });
    },
  });

  async function onSubmit(data) {
    data["projectid"] = id;
    data["files"] = files;
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        files: Array.from(files).map((file) => file.name),
        prompt: data.prompt,
      },
    ]);
    document.getElementById("file-upload").value = [];
    document.getElementById("prompt").value = "";
    setFiles([]);
    mutate(data);
  }
  console.log(messages);

  if (isPending) {
    return (
      <main className="w-full flex flex-col items-center justify-around"></main>
    );
  }
  // TODO: placeholder
  const project = projects[projects.findIndex((item) => item.id == id)];

  if (project.state == "ready") {
    return (
      <main className="w-full flex flex-col items-center justify-between p-4">
        <h1 className="text-foreground text-3xl font-bold p-2">
          {project.name}
        </h1>
        <ScrollArea className="w-3/4 bg-secondary rounded-md grow flex flex-col p-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex flex-row ${message.role == "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`flex flex-col ${message.role == "user" ? "align-bottom" : "align-top"} space-y-2`}
              >
                {message.files.map((file, i) => (
                  <div
                    className={`inline-flex ${message.role == "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      key={i}
                      className="bg-zinc-400/50 border rounded-sm flex flex-row items-center space-x-2 p-1"
                    >
                      <FaFileAlt />
                      <p>{file}</p>
                    </div>
                  </div>
                ))}
                <div
                  className={`inline-flex ${message.role == "user" ? "justify-end" : "justify-start"}`}
                >
                  <p
                    className={`${message.role == "user" ? "bg-zinc-400" : "bg-cyan-300"} max-w-60 p-2 rounded-md min-w-10`}
                  >
                    {message.prompt}
                  </p>
                </div>
              </div>
            </div>
          ))}
          {messages.length == 0 ? (
            <h1 className="text-2xl w-72 ml-8 absolute bottom-10 left-[calc(50%-144px)] ">
              Should we get started?
            </h1>
          ) : (
            ""
          )}
        </ScrollArea>
        <div className="min-w-[768px] flex flex-col items-center space-y-6">
          <form onSubmit={handleSubmit(onSubmit)} className="w-full space-y-4">
            <div className="relative">
              <div className="flex flex-col space-y-2 w-full absolute bottom-2 left-0">
                {files.length != 0 ? (
                  <Button
                    className="w-1/4 shadow-sm bg-primary/50 backdrop-blur supports-[backdrop-filter]:bg-primary/60"
                    onClick={() => {
                      document.getElementById("file-upload").value = [];
                      setFiles([]);
                    }}
                  >
                    Clear file upload
                  </Button>
                ) : (
                  ""
                )}
                {Array.from(files).map((file, idx) => (
                  <div
                    key={idx}
                    className="bg-secondary/80 p-2 w-1/2 rounded-md border-2 flex flex-row items-center space-x-2 shadow-sm backdrop-blur-sm supports-[backdrop-filter]:bg-secondary/60"
                  >
                    <FaFileAlt />
                    <p>{file.name}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="w-full flex flex-row items-center space-x-4 rounded-full border-2 border-border p-2">
              <Label className="m-0">
                <input
                  {...register("files[]")}
                  type="file"
                  id="file-upload"
                  multiple
                  hidden
                  onChange={(e) => {
                    console.log(e.target.files);
                    setFiles(e.target.files);
                  }}
                />
                <div className="w-[56px] h-[56px] rounded-full bg-secondary border-2 flex flex-col items-center justify-center hover:cursor-pointer hover:scale-105 transition-transform active:scale-95">
                  <GoPaperclip className="w-[32px] h-[32px]" />
                </div>
              </Label>
              <Input
                {...register("prompt")}
                id="prompt"
                className="w-full text-2xl rounded-none font-light py-6 px-5 border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                type="text"
                placeholder={`Ask ${project.name} a question`}
              />
              <button
                type="submit"
                className="min-w-[56px] h-[56px] rounded-full bg-blue-200 border-2 flex flex-col items-center justify-center hover:cursor-pointer hover:scale-110 transition-transform active:scale-90"
              >
                {mutatePending ? (
                  <AiOutlineLoading className="w-[32px] h-[32px] animate-spin" />
                ) : (
                  <IoIosSend className="w-[32px] h-[32px]" />
                )}
              </button>
            </div>
          </form>
          <Button variant="outline" className="" asChild>
            <Link to="edit">Edit and fine tune this model</Link>
          </Button>
          <Toaster />
        </div>
      </main>
    );
  }

  return (
    <main className="w-full flex flex-col items-center justify-around">
      <h1 className="text-foreground text-3xl font-bold">{project.name}</h1>
      <p>
        This model is currently building. Please wait a minute for AlphaGPT to
        finish building your model.
      </p>
      <div className="min-w-[768px] flex flex-col items-center space-y-6">
        <Skeleton className="min-w-[350px] h-16" />
        <Skeleton className="min-w-[768px] h-20" />
      </div>
    </main>
  );
}
