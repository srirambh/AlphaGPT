import { Link } from "react-router-dom";
import { Button } from "./components/ui/button";
import { ScrollArea } from "./components/ui/scroll-area";
import { Separator } from "./components/ui/separator";
import { useQuery } from "@tanstack/react-query";
import { getModels } from "./requests";
import { projects } from "./db/db";
import { useEffect, useState } from "react";
import { Progress } from "./components/ui/progress";
import { Skeleton } from "./components/ui/skeleton";

export default function Sidebar() {
  const [progress, setProgress] = useState(13);
  const { data, isPending } = useQuery({
    queryKey: ["models"],
    queryFn: getModels,
  });
  useEffect(() => {
    const timer = setTimeout(() => setProgress(77), 3000);
    return () => clearTimeout(timer);
  }, []);
  return (
    <div className="min-w-36 border-b border-border/40 bg-secondary/95 backdrop-blur supports-[backdrop-filter]:bg-secondary/60 z-10 flex flex-col items-center space-y-10 pt-10 shadow-lg">
      <Button
        className="min-h-24 min-w-24 hover:scale-105 transition-transform bg-zinc-500 hover:bg-zinc-500/70 border-2 shadow-md active:scale-95"
        asChild
      >
        <Link to="/">
          <p className="text-primary-foreground font-medium text-5xl">α</p>
        </Link>
      </Button>
      <Separator className="w-[120px]" />
      <ScrollArea className="w-full h-full">
        <div className="flex flex-col space-y-6 items-center">
          {isPending ? (
            <Skeleton className="h-[80px] w-[80px]" />
          ) : (
            projects.map(
              //TODO: Placeholder -> change projects to data
              (project, idx: number) =>
                project.state == "ready" ? (
                  <Button
                    key={idx}
                    className="h-[80px] w-[80px] hover:scale-105 transition-transform hover:bg-zinc-400/70 active:scale-95 bg-zinc-400 border-2 shadow-sm"
                    asChild
                  >
                    <Link to={`/${project.id}`}>
                      <p className="text-secondary-foreground">
                        {project.name}
                      </p>
                    </Link>
                  </Button>
                ) : (
                  <Button
                    key={idx}
                    className="h-[80px] w-[80px] flex flex-col items-center justify-around bg-zinc-300 hover:bg-zinc-300/90 active:scale-95 transition-transform"
                    asChild
                  >
                    <Link to={`/${project.id}`}>
                      <p className="text-secondary-foreground">
                        {project.name}
                      </p>
                      <Progress value={progress} className="h-[10px] border" />
                    </Link>
                  </Button>
                ),
            )
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
