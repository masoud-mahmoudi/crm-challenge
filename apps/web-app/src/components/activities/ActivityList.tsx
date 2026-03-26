import type { GraphqlActivity } from '../../types/crm';
import { formatDateTime } from '../../utils/formatting';
import { Badge } from '../badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../card';

interface ActivityListProps {
  activities: GraphqlActivity[];
}

export function ActivityList({ activities }: ActivityListProps) {
  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Activities</CardTitle>
        <CardDescription>
          Follow-up activity appears here as async workflows complete or users add activity records.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3">
        {activities.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border bg-muted/30 p-6 text-sm text-muted-foreground">
            No activities yet. Keep this page open or refresh to watch eventual updates arrive.
          </div>
        ) : (
          activities.map((activity) => (
            <div key={activity.id} className="rounded-2xl border border-border bg-card p-4 shadow-sm">
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-medium">{activity.summary}</p>
                    <Badge variant="outline">{activity.type}</Badge>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Status: Recorded · Due date: —
                  </p>
                </div>
                <p className="text-sm text-muted-foreground">{formatDateTime(activity.createdAt)}</p>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
