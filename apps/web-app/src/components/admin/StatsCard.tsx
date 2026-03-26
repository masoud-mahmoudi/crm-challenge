import * as React from "react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../card";
import { cn } from "../utils";

export type StatsCardProps = {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down";
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
};

export function StatsCard({ title, value, change, trend, icon: Icon }: StatsCardProps) {
  const TrendIcon = trend === "up" ? ArrowUpRight : ArrowDownRight;
  const trendTone = trend === "up" ? "text-emerald-600" : "text-red-500";

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-4">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">{title}</p>
          <CardTitle className="text-2xl font-semibold leading-tight">{value}</CardTitle>
        </div>
        {/* <Badge className="bg-primary/10 text-primary border-0"> */}
        <div className="rounded-full bg-primary/10 p-3">
          <Icon className="h-6 w-6" />
        </div>
        {/* </Badge> */}
      </CardHeader>
      <CardContent>
        <div className={cn("flex items-center gap-2 text-sm font-medium", trendTone)}>
          <TrendIcon className="h-4 w-4" />
          <span>{change}</span>
        </div>
      </CardContent>
    </Card>
  );
}
