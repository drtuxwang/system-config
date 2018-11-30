{{- define "chart.name" -}}
{{-   .Chart.Name -}}
{{- end -}}

{{- define "chart.appname" -}}
{{-   $name := .Chart.Name -}}
{{-   if contains $name .Release.Name -}}
{{-     .Release.Name | trunc 53 | trimSuffix "-" -}}
{{-   else -}}
{{-     printf "%s-%s" .Release.Name $name | trunc 53 | trimSuffix "-" -}}
{{-   end -}}
{{- end -}}

{{- define "chart.image.server" -}}
{{-   .Values.image.server -}}
{{- end -}}
