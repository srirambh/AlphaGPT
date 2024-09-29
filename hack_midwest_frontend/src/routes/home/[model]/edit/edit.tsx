import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getModel } from "../requests";
import { projects } from "@/db/db";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { postFile } from "./requests";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { FaFileAlt } from "react-icons/fa";

export default function EditDashboard() {
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState();
  const { id } = useParams();
  const { data, isPending } = useQuery({
    queryKey: ["model", id],
    queryFn: getModel,
  });

  const { register, handleSubmit } = useForm();
  const { mutate } = useMutation({
    mutationFn: postFile,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["model", id] });
      console.log("postFile success!");
    },
  });
  // async function onSubmit(data: any) {
  //   mutate(data);
  // }

  // TODO: placeholder
  const project = projects[projects.findIndex((item) => item.id == id)];

  if (isPending) {
    return (
      <main className="w-full flex flex-col items-center pt-10 space-y-16">
        <h1 className="text-foreground text-3xl font-bold">{project.name}</h1>
        <p>Loading...</p>
      </main>
    );
  }
  return (
    <main className="w-full flex flex-col items-center pt-10 space-y-16">
      <h1 className="text-foreground text-3xl font-bold">{project.name}</h1>
      <section className="w-2/3 space-y-6">
        <h1>Worker LLMs</h1>
        <Accordion type="single" collapsible className="w-full border-t">
          {project.workers.map((worker, idx) => {
            async function onSubmit(data: any) {
              console.log(data);
              data["workerid"] = worker.id;
              data["projectid"] = id;
              mutate(data);
            }
            return (
              <AccordionItem value={worker.id} key={idx}>
                <AccordionTrigger
                  onClick={() =>
                    setSelectedFile(
                      worker.files.length ? worker.files[0].name : "No file",
                    )
                  }
                >
                  <p className="w-1/2">{worker.id}</p>
                  <p
                    className={`${worker.status == "online" ? "text-green-600" : worker.status == "restarting" ? "text-orange-500" : "text-red-600"}`}
                  >
                    {worker.status}
                  </p>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="flex flex-row space-x-4">
                    <div className="min-w-60">
                      <div className="flex flex-col space-y-2 w-full">
                        {worker.files.map((file) => (
                          <div
                            className={`p-2 rounded-md border-2 hover:cursor-pointer flex flex-row items-center space-x-2 ${file.name == selectedFile ? "bg-secondary" : ""}`}
                            onClick={() => setSelectedFile(file.name)}
                          >
                            <FaFileAlt />
                            <p>{file.name}</p>
                          </div>
                        ))}
                      </div>
                      <p className="mt-4 mb-2">Upload a file</p>
                      <form
                        onSubmit={handleSubmit(onSubmit)}
                        className="flex flex-col space-y-4 w-full"
                      >
                        <Input
                          {...register("file")}
                          type="file"
                          className="hover:cursor-pointer"
                        />
                        <Button type="submit">Upload</Button>
                      </form>
                    </div>
                    <div className="w-full bg-secondary h-72 inline-flex items-center justify-center rounded-md">
                      <p>{selectedFile} graph content</p>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            );
          })}
        </Accordion>
      </section>
    </main>
  );
}
