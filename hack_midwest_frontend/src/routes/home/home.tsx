import { Input } from "@/components/ui/input";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { postModel } from "./requests";
import { useForm } from "react-hook-form";
import { Label } from "@/components/ui/label";

export default function Home() {
  const queryClient = useQueryClient();
  const { register, handleSubmit } = useForm();
  const { mutate } = useMutation({
    mutationFn: postModel,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["models"] });
      console.log("postModel success!");
    },
  });
  async function onSubmit(data: any) {
    mutate(data);
  }
  return (
    <main className="w-full flex flex-col items-center justify-around">
      <h1 className="text-foreground text-3xl font-bold">AlphaGPT</h1>
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="w-[768px] flex flex-col items-center space-y-6"
      >
        <Label htmlFor="prompt" className="text-2xl">
          Let's build your refined LLM.
        </Label>
        <Input
          id="prompt"
          {...register("prompt")}
          className="max-w-3xl rounded-full text-2xl border-2 font-light py-6 px-5"
          type="text"
          placeholder="Ask AlphaGPT for a customized LLM"
        />
      </form>
    </main>
  );
}
