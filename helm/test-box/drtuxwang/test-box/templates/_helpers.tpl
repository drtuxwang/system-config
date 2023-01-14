{{- define "chart.name" -}}
{{-   .Chart.Name -}}
{{- end -}}

{{- define "app.fullname" -}}
{{-   if .Values.fullnameOverride -}}
{{-     .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{-   else -}}
{{-     .Release.Name | trunc 63 | trimSuffix "-" -}}
{{-   end -}}
{{- end -}}

{{- define "chart.image.name" -}}
{{-   $registry_name := .Values.image.registry -}}
{{-   $repository_ame := .Values.image.repository -}}
{{-   $tag := .Values.image.tag | toString -}}
{{-   printf "%s/%s:%s" $registry_name $repository_ame $tag -}}
{{- end -}}
