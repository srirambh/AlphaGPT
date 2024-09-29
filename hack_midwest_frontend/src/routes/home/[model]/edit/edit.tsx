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

export default function EditDashboard() {
  const queryClient = useQueryClient();
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
        <Accordion type="single" collapsible className="w-full">
          {project.workers.map((worker, idx) => {
            async function onSubmit(data: any) {
              console.log(data);
              data["workerid"] = worker.id;
              data["projectid"] = id;
              mutate(data);
            }
            return (
              <AccordionItem value={worker.id} key={idx}>
                <AccordionTrigger>
                  <p className="w-1/2">{worker.id}</p>
                  <p
                    className={`${worker.status == "online" ? "text-green-600" : worker.status == "restarting" ? "text-orange-500" : "text-red-600"}`}
                  >
                    {worker.status}
                  </p>
                </AccordionTrigger>
                <AccordionContent>
                  Upload a file
                  <form
                    onSubmit={handleSubmit(onSubmit)}
                    className="flex flex-col space-y-4 w-1/4"
                  >
                    <Input {...register("file")} type="file" />
                    <Button type="submit">Upload</Button>
                  </form>
                </AccordionContent>
              </AccordionItem>
            );
          })}
        </Accordion>
      </section>
    </main>
  );
}
