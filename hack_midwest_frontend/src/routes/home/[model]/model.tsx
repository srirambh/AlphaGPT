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

export default function ModelDashboard() {
  const [files, setFiles] = useState<File[]>([]);
  console.log(files);
  const queryClient = useQueryClient();
  const { id } = useParams();
  const { register, handleSubmit } = useForm();

  const { data, isPending } = useQuery({
    queryKey: ["model", id],
    queryFn: getModel,
  });
  const { mutate } = useMutation({
    mutationFn: filePost,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["model", id] });
      console.log("filePost success!");
    },
  });

  async function onSubmit(data) {
    data["projectid"] = id;
    data["file"] = files;
    mutate(data);
  }

  if (isPending) {
    return (
      <main className="w-full flex flex-col items-center justify-around"></main>
    );
  }
  // TODO: placeholder
  const project = projects[projects.findIndex((item) => item.id == id)];

  if (project.state == "ready") {
    return (
      <main className="w-full flex flex-col items-center justify-around">
        <h1 className="text-foreground text-3xl font-bold">{project.name}</h1>
        <div className="min-w-[768px] flex flex-col items-center space-y-6">
          {files.length == 0 ? (
            <Label htmlFor="prompt" className="text-2xl">
              Should we get started?
            </Label>
          ) : (
            <div className="flex flex-col w-full space-y-2">
              {Array.from(files).map((file, idx) => (
                <div
                  key={idx}
                  className="bg-secondary p-2 w-1/2 rounded-md border-2"
                >
                  {file.name}
                </div>
              ))}
            </div>
          )}
          <form
            className="w-full flex flex-row items-center space-x-4 rounded-full border-2 border-border p-2"
            onSubmit={handleSubmit(onSubmit)}
          >
            <Label className="m-0">
              <input
                {...register("file[]")}
                type="file"
                id="file-upload"
                multiple
                hidden
                onChange={(e) => {
                  console.log(e.target.files);
                  setFiles(e.target.files);
                }}
              />
              <div className="w-[56px] h-[56px] rounded-full bg-secondary border-2 flex flex-col items-center justify-center hover:cursor-pointer">
                <p className="text-sm">File icon</p>
              </div>
            </Label>
            <Input
              {...register("prompt")}
              id="prompt"
              className="w-full text-2xl rounded-none font-light py-6 px-5 border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
              type="text"
              placeholder={`Ask ${project.name} a question`}
            />
          </form>
          <Button variant="outline" className="" asChild>
            <Link to="edit">Edit and fine tune this model</Link>
          </Button>
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
